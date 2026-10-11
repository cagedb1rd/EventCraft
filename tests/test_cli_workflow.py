import json
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

from eventcraft.cli import main
from eventcraft.copywriting import campaign
from eventcraft.extractors import extract, parse_text
from eventcraft.recommendation import rank
from eventcraft.schema import Event

ROOT = Path(__file__).resolve().parents[1]


def test_missing_unattended_exit_and_no_output(tmp_path):
    source = tmp_path / "missing.json"
    source.write_text('{"title":"No date"}')
    dest = tmp_path / "bad"
    assert main(["all", str(source), "--auto-style", "--output", str(dest)]) == 2
    assert not dest.exists()


def test_no_unlabelled_website_registration_and_demo():
    event = parse_text("# Example\n主办方网站 https://example.org\n虚构活动")
    assert event.registration_url is None
    assert event.demo


def test_default_values_not_falsely_provided(tmp_path):
    source = tmp_path / "minimal.json"
    source.write_text('{"title":"explicit title"}')
    event = extract(source)
    assert set(event.sources) == {"title"}


@pytest.mark.render
def test_interactive_one_fact_question_then_one_batch(tmp_path, chromium):
    source = tmp_path / "incomplete.md"
    source.write_text("# 校园讲座\n活动类型：lecture\n虚构活动", encoding="utf-8")
    reply = json.dumps({"start": "2026-11-01T14:00", "timezone": "Asia/Shanghai",
                        "venue": "示例楼", "registration": "无需报名"}, ensure_ascii=False)
    from eventcraft.renderer import batch_render
    with patch("builtins.input", side_effect=[reply, "2"]) as question, patch("eventcraft.cli.batch_render", wraps=batch_render) as batch:
        assert main(["all", str(source), "--interactive", "--state", str(tmp_path / "state"), "--output", str(tmp_path / "final")]) == 0
        assert question.call_count == 2
        assert batch.call_count == 1
    result = json.loads((tmp_path / "final/event.json").read_text(encoding="utf-8"))
    assert "venue" in result["confirmed_fields"]


@pytest.mark.render
def test_cli_next_all_and_reference_replay(tmp_path, chromium):
    source = str(ROOT / "examples/inputs/lecture.json")
    state_dir = tmp_path / "state"
    assert main(["recommend", source, "--output", str(state_dir)]) == 0
    first = json.loads((state_dir / "state.json").read_text(encoding="utf-8"))
    assert main(["recommend", source, "--output", str(state_dir), "--next"]) == 0
    second = json.loads((state_dir / "state.json").read_text(encoding="utf-8"))
    assert not {s["style_id"] for s in first["recommendations"]} & {s["style_id"] for s in second["recommendations"]}
    assert main(["recommend", source, "--output", str(tmp_path / "all"), "--all"]) == 0
    assert len(json.loads((tmp_path / "all/state.json").read_text(encoding="utf-8"))["displayed"]) == 10
    ref = tmp_path / "ref.png"
    Image.new("RGB", (30, 30), "#003344").save(ref)
    assert main(["render", source, "--style-reference", str(ref), "--style-description", "复古印刷风", "--output", str(tmp_path / "custom")]) == 0
    assert main(["render", source, "--style-override", str(tmp_path / "custom/style_override.json"), "--output", str(tmp_path / "replay")]) == 0
    custom = json.loads((tmp_path / "custom/manifest.json").read_text(encoding="utf-8"))
    replay = json.loads((tmp_path / "replay/manifest.json").read_text(encoding="utf-8"))
    assert custom["base_style"] == replay["base_style"] == "retro-print"
    assert custom["palette"] == replay["palette"]


def test_profiles_resources_consistent():
    from eventcraft.recommendation import catalog
    public = json.loads((ROOT / "assets/styles/style-profiles.json").read_text(encoding="utf-8"))
    assert public == catalog()
    for sid in public["styles"]:
        assert (ROOT / f"references/style-guides/{sid}.md").is_file()
        assert json.loads((ROOT / f"assets/styles/{sid}.json").read_text(encoding="utf-8"))["id"] == sid


def test_long_copy_and_english_unknown_fields():
    event = Event(title="Long title " * 20, start="2026-01-01T14:00", timezone="Asia/Shanghai", online_platform="Example online", registration="No registration", language="en")
    assert len(campaign(event)["short.txt"].splitlines()[0]) <= 90
    assert event.title in campaign(event)["social.md"]
    assert "students" not in str(rank(event))


@pytest.mark.render
def test_pdf_text_input_roundtrip(tmp_path, chromium):
    from eventcraft.renderer import batch_render
    event = extract(ROOT / "examples/inputs/dinner.json")
    batch_render(event, tmp_path / "package", "luxury-elegant", instance=chromium)
    from eventcraft.extractors import read_text
    text = read_text(tmp_path / "package/invite_letter.pdf")
    assert event.title in text and event.venue in text
    assert event.registration in text
    scanned = tmp_path / "scanned.pdf"
    from pypdf import PdfWriter
    writer = PdfWriter()
    writer.add_blank_page(595, 842)
    with scanned.open("wb") as stream:
        writer.write(stream)
    with pytest.raises(ValueError, match="Scanned"):
        extract(scanned)
