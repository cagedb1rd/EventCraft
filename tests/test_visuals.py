"""Asset integrity, relocation, invitation shapes and composed QR regression checks."""
import hashlib
import json
from pathlib import Path

import cv2
import pytest
from PIL import Image
from pypdf import PdfReader

from eventcraft.cli import main
from eventcraft.extractors import extract
from eventcraft.renderer import batch_render
from eventcraft.renderer.campaigns import INVITATION_SIZES, invitation_format
from eventcraft.security import write_json
from eventcraft.visuals import campaign_art, import_art, systems, visual_plan

ROOT = Path(__file__).resolve().parents[1]


def test_all_bundled_art_is_original_verified_and_packaged():
    records = json.loads((ROOT / "assets/generated-art.json").read_text(encoding="utf-8"))
    assert len(records) == 10
    for sid in systems():
        path = ROOT / records[sid]["asset"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == records[sid]["sha256"]
        with Image.open(path) as im:
            assert min(im.size) >= 768


def test_host_bridge_receipt_is_bound_to_facts_and_bytes(event, tmp_path):
    plan = tmp_path / "plan.json"
    write_json(plan, visual_plan(event, "tech-gradient"))
    source = ROOT / "eventcraft/data/art/tech-gradient.png"
    import_art(plan, source, tmp_path / "art", "codex-imagegen")
    event.assets.visual_receipt = str(tmp_path / "art/receipt.json")
    assert campaign_art(event, "tech-gradient")[1]["provenance"] == "host-agent-attested"
    event.title += " changed"
    with pytest.raises(ValueError, match="mismatch"):
        campaign_art(event, "tech-gradient")
    event.title = event.title.removesuffix(" changed")
    (tmp_path / "art/tech-gradient.png").write_bytes(source.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="hash mismatch"):
        campaign_art(event, "tech-gradient")


def test_require_art_does_not_silently_generate_or_charge(tmp_path):
    assert main(["all", str(ROOT / "examples/inputs/web-summit.json"), "--style", "tech-gradient",
                 "--require-art", "--output", str(tmp_path / "no-art")]) == 2
    assert not (tmp_path / "no-art").exists()


@pytest.mark.render
@pytest.mark.parametrize("form", INVITATION_SIZES)
def test_native_invitation_shape_pdf_and_real_qr(form, event, chromium, tmp_path):
    event.qr_policy = 'show'
    event.invitation_format = form
    style = "luxury-elegant" if form == "formal-card" else "tech-gradient"
    dest = tmp_path / form
    manifest = batch_render(event, dest, style, instance=chromium)
    assert manifest["invitation_format"] == form
    assert Image.open(dest / "invitation.png").size == INVITATION_SIZES[form]
    assert len(PdfReader(dest / "invitation_print.pdf").pages) == 1
    actual = cv2.imread(str(dest / "invitation.png"))
    decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(actual)
    assert decoded == event.registration_url
    if form == "folded":
        assert len(PdfReader(dest / "invitation_folded_print.pdf").pages) == 2
        assert (dest / "invitation_outside.png").exists()


@pytest.mark.render
def test_campaign_art_export_can_relocate_and_replay(event, chromium, tmp_path):
    plan = tmp_path / "plan.json"
    write_json(plan, visual_plan(event, "tech-gradient"))
    import_art(plan, ROOT / "eventcraft/data/art/tech-gradient.png", tmp_path / "art", "codex-imagegen")
    event.assets.visual_receipt = str(tmp_path / "art/receipt.json")
    first = tmp_path / "first"
    batch_render(event, first, "tech-gradient", instance=chromium)
    public = (first / "event.json").read_text(encoding="utf-8")
    assert str(tmp_path) not in public
    replay = extract(first / "event.json")
    manifest = batch_render(replay, tmp_path / "replayed", "tech-gradient", instance=chromium)
    assert manifest["artwork"]["generator"] == "codex-imagegen"


def test_invitation_selection_follows_event_and_user(event):
    event.category = "conference"
    assert invitation_format(event, "swiss-grid") == "boarding-pass"
    event.formality = "ceremonial"
    assert invitation_format(event, "tech-gradient") == "formal-card"
    event.invitation_format = "folded"
    assert invitation_format(event, "tech-gradient") == "folded"


@pytest.mark.render
def test_numbered_choice_accepts_fresh_art_and_invitation_override(event, tmp_path):
    from eventcraft.recommendation.state import save_recommendations
    source = tmp_path / "event.json"
    write_json(source, event.model_dump())
    event = extract(source)  # Both CLI turns read the same serialized input/evidence.
    state = save_recommendations(event, tmp_path / "state")
    style = state["recommendations"][0]["style_id"]
    plan = tmp_path / "plan.json"
    write_json(plan, visual_plan(event, style))
    import_art(plan, ROOT / f"eventcraft/data/art/{style}.png", tmp_path / "art", "codex-imagegen")
    output = tmp_path / "campaign"
    assert main(["all", str(source), "--select", "1", "--state", str(tmp_path / "state"),
                 "--visual-receipt", str(tmp_path / "art/receipt.json"), "--require-art",
                 "--invitation-format", "ticket-stub", "--output", str(output)]) == 0
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["base_style"] == style
    assert manifest["invitation_format"] == "ticket-stub"
    assert manifest["selection"]["selection_source"] == "three-choice"


@pytest.mark.render
@pytest.mark.parametrize("sid", list(systems()))
def test_posters_keep_only_core_facts_on_reading_surfaces(sid, event, chromium):
    from eventcraft.renderer import asset_images, palette_for, prepare
    from eventcraft.renderer.templates import sheet_html
    page = chromium.new_page()
    try:
        _, check = prepare(page, sheet_html(event, sid, 1080, 1920, "portrait",
                            palette_for(event, sid), asset_images(event, style=sid)), 1080, 1920)
        assert len(check["reading_zones"]) == 3
        assert page.locator('.details .fact').count() == 2
        assert page.locator('.summary li').count() == 0
        assert event.registration_url not in page.locator('.sheet').text_content()
        assert page.locator('[data-field="cta"]').count() == 1
        assert page.locator('.qr img').count() == 0
        assert all(zone['background'] == 'rgba(0, 0, 0, 0)' for zone in check['reading_zones'])
    finally:
        page.close()
