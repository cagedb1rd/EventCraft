"""Capture an unsuccessful composition for visual diagnosis, never as a deliverable."""
import json
import sys
from pathlib import Path

from eventcraft.extractors import extract
from eventcraft.renderer import asset_images, browser, palette_for, prepare
from eventcraft.renderer.campaigns import INVITATION_SIZES, invitation_format
from eventcraft.renderer.templates import sheet_html
from eventcraft.validation import CHECK_SCRIPT

event = extract(Path(sys.argv[1]))
style = sys.argv[2]
kind = sys.argv[3] if len(sys.argv) > 3 else "portrait"
w, h = INVITATION_SIZES[invitation_format(event, style)] if kind == "invitation" else (1080, 1080 if kind == "square" else 1527 if kind == "print" else 1920)
with browser() as active:
    page = active.new_page()
    try:
        prepare(page, sheet_html(event, style, w, h, kind, palette_for(event, style), asset_images(event, style=style)), w, h)
    except ValueError as exc:
        print(exc)
    print(json.dumps(page.evaluate(CHECK_SCRIPT), ensure_ascii=False))
    print(page.locator('.sheet').evaluate("e=>({scroll:e.scrollHeight,client:e.clientHeight,rows:getComputedStyle(e).gridTemplateRows,sections:[...e.querySelectorAll(':scope>header,:scope>section,:scope>footer')].map(x=>({name:x.className||x.tagName,box:x.getBoundingClientRect().toJSON()}))})"))
    target = Path("tmp/visual-v2")
    target.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(target / f"debug-{style}-{kind}.png"))
