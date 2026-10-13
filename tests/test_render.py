import json
import math
import shutil
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
import pytest
from PIL import Image, ImageChops, ImageDraw
from pypdf import PdfReader

from eventcraft.cli import main, recommend
from eventcraft.extractors import extract
from eventcraft.providers.reference import analyze_references
from eventcraft.recommendation import profiles, rank
from eventcraft.recommendation.state import choose
from eventcraft.renderer import batch_render, palette_for, prepare, render_preview
from eventcraft.renderer.campaigns import INVITATION_SIZES, invitation_format
from eventcraft.renderer.templates import sheet_html
from eventcraft.schema import facts
from eventcraft.security import digest

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.render


@pytest.mark.parametrize("style", list(profiles()))
@pytest.mark.parametrize("variant", ["normal", "long-bilingual", "short-crossday"])
def test_all_layouts_and_text_bounds(style, variant, event, chromium, tmp_path):
    if variant == "long-bilingual":
        event.title = "AI Agent 实战分享会：面向跨学科创作者的工作流实践与开放协作 / Practical Creation Workshop"
        event.language = "bilingual"
    elif variant == "short-crossday":
        event.title = "相遇"
        event.end = "2026-10-27T16:30"
        event.subtitle = ""
        event.highlights = []
        event.speakers = []
    page = chromium.new_page()
    try:
        for w, h, kind in [(1080, 1920, "portrait"), (1080, 1350, "invitation"), (1080, 1080, "square")]:
            _, check = prepare(page, sheet_html(event, style, w, h, kind, palette_for(event, style), {}), w, h)
            assert check["passed"]
            if variant == "long-bilingual" and kind == "portrait" and style in {"swiss-grid", "sports-dynamic"}:
                assert check["title_layout"] == "expanded"
            if variant == "normal" and kind == "portrait" and style in {"swiss-grid", "tech-gradient"}:
                # A short CJK phrase that fits a full row should not split internally.
                assert page.locator(".title-word").filter(has_text="实战分享会").count() == 1
            if variant == "short-crossday":
                # Short headings must retain the enlarged display hierarchy.
                actual = float(check["font_sizes"][0]["size"].removesuffix("px"))
                assert actual >= {"portrait": 100, "invitation": 80, "square": 68}[kind]
            text = page.locator(".sheet").text_content()
            assert all(facts(event)[key] in text for key in ["title", "when", "where"])
            if kind == "invitation":
                assert facts(event)["registration"] in text
            else:
                assert page.locator('.summary li').count() == 0
                assert page.locator('[data-field="cta"]').count() == 1
            screenshot = tmp_path / f"{style}-{kind}.png"
            page.screenshot(path=str(screenshot))
            with Image.open(screenshot) as image:
                assert image.size == (w, h)
    finally:
        page.close()


@pytest.mark.parametrize("name", ["lecture", "launch", "birthday", "dinner", "sports"])
def test_five_complete_campaigns(name, chromium, tmp_path):
    event = extract(ROOT / f"examples/inputs/{name}.json")
    event.qr_policy = 'show' if event.registration_url else 'auto'
    style = rank(event)["style_scores"][0]["style_id"]
    manifest = batch_render(event, tmp_path / name, style, instance=chromium)
    assert manifest["batch_entry_calls"] == 1
    assert manifest["checks"]["facts"]
    for output, dimensions in [("poster_portrait.png", (1080, 1920)), ("poster_square.png", (1080, 1080)), ("invitation.png", INVITATION_SIZES[invitation_format(event, style)])]:
        with Image.open(tmp_path / name / output) as image:
            assert image.size == dimensions
            image.verify()
    for pdf in ["poster_print.pdf", "invite_letter.pdf"]:
        reader = PdfReader(tmp_path / name / pdf)
        assert len(reader.pages) >= 1
        assert abs(float(reader.pages[0].mediabox.width) - 595.28) < 1
    assert "INVITATION" not in (tmp_path / name / "poster_print.html").read_text(encoding="utf-8")
    source = json.loads((tmp_path / name / "event.json").read_text(encoding="utf-8"))
    assert source["venue"] == event.venue
    for path in (tmp_path / name / "copy").iterdir():
        assert facts(event)["when"] in path.read_text(encoding="utf-8")
    page = chromium.new_page()
    page.goto((tmp_path / name / "preview.html").as_uri())
    assert page.locator("img").count() == 3
    assert page.locator("img").evaluate_all("xs=>xs.every(i=>i.complete&&i.naturalWidth)")
    page.close()
    if event.registration_url:
        image = cv2.imread(str(tmp_path / name / "registration_qr.png"))
        decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(image)
        assert decoded == event.registration_url
        # Verify the code from the actual composed poster, including resized quiet zone.
        composed = cv2.imread(str(tmp_path / name / "poster_portrait.png"))
        decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(composed)
        assert decoded == event.registration_url
    else:
        assert not (tmp_path / name / "registration_qr.png").exists()


def test_previews_differ_same_facts_and_state(event, chromium, tmp_path):
    styles = [r["style_id"] for r in rank(event)["style_scores"][:3]]
    images = []
    for style in styles:
        path = tmp_path / (style + ".png")
        report = render_preview(event, style, path, instance=chromium)
        assert report["event_digest"] == digest(event.model_dump())
        images.append(np.asarray(Image.open(path).convert("RGB")))
    assert all(np.mean(np.abs(images[0].astype(float)-other.astype(float))) > 20 for other in images[1:])
    original = event.model_dump()
    recommend(event, tmp_path / "state")
    assert event.model_dump() == original
    selected, selection = choose(event, tmp_path / "state", "2")
    with patch("eventcraft.cli.batch_render", wraps=batch_render) as entry:
        assert main(["all", str(ROOT / "examples/inputs/lecture.json"), "--state", str(tmp_path / "state"), "--select", "2", "--output", str(tmp_path / "campaign")]) == 0
        assert entry.call_count == 1
    assert json.loads((tmp_path / "campaign/manifest.json").read_text(encoding="utf-8"))["base_style"] == selected
    assert selection["selection_source"] == "three-choice"


def test_logo_hero_photo_user_qr_preserved(event, chromium, tmp_path):
    import base64

    from eventcraft.renderer import asset_images
    for name in ["logo", "hero_image", "speaker_photo", "qr_image"]:
        source = tmp_path / (name + ".png")
        Image.new("RGB", (140, 70), "#003344").save(source)
        setattr(event.assets, name, str(source))
    images = asset_images(event)
    for name in ["logo", "hero_image", "speaker_photo", "qr_image"]:
        key = "qr" if name == "qr_image" else name
        assert base64.b64decode(images[key].split(",", 1)[1]) == (tmp_path / (name + ".png")).read_bytes()
    batch_render(event, tmp_path / "bundle", "swiss-grid", instance=chromium)
    assert (tmp_path / "bundle/registration_qr.png").read_bytes() == (tmp_path / "qr_image.png").read_bytes()
    page = chromium.new_page()
    page.goto((tmp_path / "bundle/poster_portrait.html").as_uri())
    assert page.locator("[data-asset]").evaluate_all("es=>es.every(e=>getComputedStyle(e).objectFit==='contain')")
    page.close()


def test_reference_batch_no_private_image_copy(event, chromium, tmp_path):
    ref = tmp_path / "private.png"
    Image.new("RGB", (150, 150), "#264635").save(ref)
    override = analyze_references(event, [str(ref)], "luxury-elegant")
    manifest = batch_render(event, tmp_path / "custom", "tech-gradient", override=override, instance=chromium)
    assert manifest["style"] == "custom"
    assert manifest["base_style"] == "luxury-elegant"
    assert (tmp_path / "custom/style_override.json").is_file()
    assert not (tmp_path / "custom/private.png").exists()


def test_unattended_missing_fails_and_draft_marked(event, chromium, tmp_path):
    event.start = None
    event.registration_url = None
    event.registration = None
    with pytest.raises(ValueError, match="confirmation"):
        batch_render(event, tmp_path / "bad", "tech-gradient", instance=chromium)
    assert not (tmp_path / "bad").exists()
    manifest = batch_render(event, tmp_path / "draft", "tech-gradient", draft=True, instance=chromium)
    assert manifest["draft"] and not manifest["publishable"]
    assert "DRAFT" in (tmp_path / "draft/poster_portrait.html").read_text(encoding="utf-8")
    assert not (tmp_path / "draft/registration_qr.png").exists()


def test_html_injection_escaped(event, chromium, tmp_path):
    event.title = '<img src=x onerror="alert(1)"> Example'
    page = chromium.new_page()
    _, check = prepare(page, sheet_html(event, "swiss-grid", 1080, 1920, "portrait", palette_for(event, "swiss-grid"), {}), 1080, 1920)
    assert page.locator("h1 img").count() == 0
    assert check["passed"]
    page.close()


def test_explicit_non_top_style_and_auto_cli(tmp_path):
    source = str(ROOT / "examples/inputs/birthday.json")
    assert main(["render", source, "--style", "retro-print", "--output", str(tmp_path / "retro")]) == 0
    assert main(["all", source, "--auto-style", "--output", str(tmp_path / "auto")]) == 0
    assert json.loads((tmp_path / "auto/manifest.json").read_text(encoding="utf-8"))["selection"]["selection_source"] == "auto-highest"


def repeatable_pixels(left, right, text_boxes):
    """Allow only sparse, low-amplitude glyph rasterization noise, never layout changes."""
    if left.size != right.size or left.mode != right.mode:
        return False
    delta = np.asarray(ImageChops.difference(left, right))
    changed = np.any(delta != 0, axis=2)
    if not changed.any():
        return True
    # Real CI evidence: 107 pixels in one glyph, maximum channel delta 8/255.
    # Also require exact HTML, facts and layout in the calling integration test.
    if delta.max() > 8 or changed.sum() > max(1, left.width * left.height // 10000):
        return False
    mask = Image.new("1", left.size)
    draw = ImageDraw.Draw(mask)
    for box in text_boxes:
        r = box["rect"]
        draw.rectangle((math.floor(r["x"]), math.floor(r["y"]),
                        math.ceil(r["x"] + r["w"]) - 1, math.ceil(r["y"] + r["h"]) - 1), fill=1)
    return not np.any(changed & ~np.asarray(mask))


@pytest.mark.parametrize("variation,expected", [
    ("identical", True), ("glyph-edge", True), ("strong-change", False),
    ("background-change", False), ("large-change", False),
])
def test_repeatable_pixels_rejects_real_visual_changes(variation, expected):
    left = Image.new("RGB", (256, 256), (100, 100, 100))
    right = left.copy()
    if variation == "glyph-edge":
        right.putpixel((10, 10), (108, 105, 103))
    elif variation == "strong-change":
        right.putpixel((10, 10), (109, 100, 100))
    elif variation == "background-change":
        right.putpixel((200, 200), (108, 105, 103))
    elif variation == "large-change":
        ImageDraw.Draw(right).rectangle((10, 10, 25, 25), fill=(108, 105, 103))
    boxes = [{"rect": {"x": 0, "y": 0, "w": 40, "h": 40}}]
    assert repeatable_pixels(left, right, boxes) == expected


def test_deterministic_re_render(event, chromium, tmp_path):
    first = batch_render(event, tmp_path / "first", "luxury-elegant", instance=chromium)
    second = batch_render(event, tmp_path / "second", "luxury-elegant", instance=chromium)
    assert first["event_digest"] == second["event_digest"]
    assert first["artwork"] == second["artwork"]
    assert first["checks"] == second["checks"]
    for source in (tmp_path / "first").glob("*.html"):
        assert source.read_bytes() == (tmp_path / "second" / source.name).read_bytes()
    with Image.open(tmp_path / "first/poster_portrait.png") as left, Image.open(tmp_path / "second/poster_portrait.png") as right:
        difference = ImageChops.difference(left, right)
        bounds = difference.getbbox()
        matches = repeatable_pixels(left, right, first["checks"]["layouts"]["poster_portrait"]["text_boxes"])
        if not matches:
            diagnostics = ROOT / "output/ci-diagnostics/deterministic-render"
            diagnostics.mkdir(parents=True, exist_ok=True)
            for name in ["first", "second"]:
                for filename in ["poster_portrait.png", "poster_portrait.html", "manifest.json"]:
                    shutil.copyfile(tmp_path / name / filename, diagnostics / f"{name}-{filename}")
            difference.save(diagnostics / "difference.png")
        assert matches, f"Visual change beyond sparse glyph antialiasing: {bounds}"


def test_rerender_removes_obsolete_qr_only(event, chromium, tmp_path):
    output = tmp_path / "package"
    batch_render(event, output, "swiss-grid", instance=chromium)
    extra = output / "user-note.txt"
    extra.write_text("keep")
    event.registration_url = None
    event.registration = "无需报名"
    batch_render(event, output, "swiss-grid", instance=chromium)
    assert not (output / "registration_qr.png").exists()
    assert extra.read_text() == "keep"


@pytest.mark.render
def test_measured_font_box_expands_tight_title_leading(event, chromium):
    page = chromium.new_page()
    try:
        html = sheet_html(event, "editorial-minimal", 1080, 1920, "portrait",
                          palette_for(event, "editorial-minimal"), {})
        html = html.replace("<h1 ", '<h1 style="line-height:0.5" ', 1)
        _, report = prepare(page, html, 1080, 1920)
        assert report["passed"]
        assert page.locator("h1").evaluate("""e=>{
          const s=getComputedStyle(e),c=document.createElement('canvas').getContext('2d');
          c.font=s.font;const m=c.measureText(e.textContent);
          return parseFloat(s.lineHeight)>=m.fontBoundingBoxAscent+m.fontBoundingBoxDescent;
        }""")
    finally:
        page.close()
