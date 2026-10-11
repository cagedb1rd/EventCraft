import base64
import json
from unittest.mock import MagicMock

import pytest
from PIL import Image, PngImagePlugin

from eventcraft.providers import OpenAIProvider
from eventcraft.providers.reference import analyze_references
from eventcraft.security import image_uri
from eventcraft.validation import contrast, safe_palette


def test_offline_palette_multiple_private_and_deterministic(event, tmp_path):
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("secret", "private-name@example.org")
    ref = tmp_path / "private.png"
    Image.new("RGB", (300, 400), "#325864").save(ref, pnginfo=metadata)
    second = tmp_path / "other.png"
    Image.new("RGB", (200, 100), "#e8cfad").save(second)
    result = analyze_references(event, [str(ref), str(second)], "editorial-minimal", description="留白衬线")
    assert result.mode == "palette-only"
    assert "#325864" in result.colors
    assert result.typography == result.grid == ""
    assert "private-name" not in result.model_dump_json()
    assert result == analyze_references(event, [str(ref), str(second)], "editorial-minimal", description="留白衬线")
    event.style = "retro-print"
    assert analyze_references(event, [str(ref)], "tech-gradient").base_style == "retro-print"


def test_broken_large_and_too_many_references(event, tmp_path):
    bad = tmp_path / "bad.png"
    bad.write_bytes(b"corrupt")
    with pytest.raises(OSError):
        analyze_references(event, [str(bad)], "swiss-grid")
    large = tmp_path / "large.png"
    Image.new("1", (6000, 5000)).save(large)
    with pytest.raises(ValueError, match="megapixel"):
        image_uri(large)
    with pytest.raises(ValueError):
        analyze_references(event, [str(bad)] * 6, "swiss-grid")


def test_vision_contract_and_explicit_style(event, tmp_path):
    ref = tmp_path / "ref.png"
    Image.new("RGB", (30, 30), "blue").save(ref)
    provider = MagicMock()
    provider.structured.return_value = {
        "base_style": "luxury-elegant", "colors": ["#123456", "#eeeeee"],
        "typography": "serif hierarchy", "grid": "center axis", "density": "low",
        "decoration": "fine lines", "atmosphere": "formal",
    }
    result = analyze_references(event, [str(ref)], "tech-gradient", provider=provider)
    assert result.mode == "vision" and result.base_style == "luxury-elegant"
    assert len(result.reference_hashes) == 1
    event.style = "sports-dynamic"
    assert analyze_references(event, [str(ref)], "tech-gradient", provider=provider).base_style == "sports-dynamic"
    provider.structured.return_value["base_style"] = "unknown"
    event.style = None
    with pytest.raises(ValueError):
        analyze_references(event, [str(ref)], "tech-gradient", provider=provider)


def test_network_opt_in_and_key(monkeypatch):
    with pytest.raises(ValueError, match="allow-network"):
        OpenAIProvider()
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="not configured"):
        OpenAIProvider(allow_network=True)


def test_actual_http_payload_contract(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_API_KEY", "unit-test-placeholder")
    responses = [
        {"output": [{"content": [{"type": "output_text", "text": '{"title":"source only"}'}]}]},
        {"data": [{"b64_json": base64.b64encode(b"image-contract-bytes").decode()}]},
    ]
    captured = []
    class Reply:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def read(self, limit):
            return json.dumps(responses.pop(0)).encode()
    def fake_open(request, timeout):
        captured.append((request.full_url, json.loads(request.data)))
        return Reply()
    monkeypatch.setattr("urllib.request.urlopen", fake_open)
    provider = OpenAIProvider(allow_network=True)
    assert provider.structured([{"type": "input_text", "text": "x"}], {"type": "object"}, "test")["title"] == "source only"
    assert provider.generate_image("original shapes", tmp_path / "hero.png").read_bytes() == b"image-contract-bytes"
    assert captured[0][0].endswith("/responses")
    assert captured[1][1]["model"] == "gpt-image-1"
    assert "no text" in captured[1][1]["prompt"]


def test_contrast_and_brand_precedence(event, tmp_path):
    palette = safe_palette(["#ffffff", "#eeeeee", "#ffff00"], [], [])
    assert contrast(palette[0], palette[1]) >= 4.5
    # Decorative accent can be light; factual labels use a readable separate token.
    assert palette[2] == "#ffff00"
    ref = tmp_path / "ref.png"
    Image.new("RGB", (30, 30), "blue").save(ref)
    event.brand.colors = ["#003344", "#eeeeff"]
    assert analyze_references(event, [str(ref)], "swiss-grid").colors == event.brand.colors
