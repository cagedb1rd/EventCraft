"""Transactional Chromium batch renderer; no network assets and no fake image generation."""

import base64
import hashlib
import io
import os
import tempfile
import time
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path

import qrcode
from PIL import Image
from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter

from ..copywriting import campaign
from ..providers.reference import StyleOverride
from ..recommendation import profiles, rank, resolve_style
from ..schema import Event, facts, issues
from ..security import digest, image_uri, write_json
from ..validation import CHECK_SCRIPT, FIT_SCRIPT, contrast, safe_palette
from ..visuals import campaign_art, systems
from .campaigns import INVITATION_SIZES, invitation_format, invitation_html
from .templates import escape, letter_html, sheet_html

SIZES = {"poster_portrait": (1080, 1920, "portrait"), "poster_square": (1080, 1080, "square"),
         "invitation": (1080, 1350, "invitation")}
_active_browser = ContextVar("eventcraft_browser", default=None)


@contextmanager
def browser():
    shared = _active_browser.get()
    if shared is not None:
        yield shared
        return
    with sync_playwright() as playwright:
        executable = os.environ.get("EVENTCRAFT_BROWSER")
        # Use software rasterization and grayscale text antialiasing so GPU/font
        # cache state cannot change pixels between identical campaign exports.
        options = {"headless": True, "timeout": 20000,
                   "args": ["--disable-gpu", "--disable-lcd-text"]}
        if executable:
            options["executable_path"] = executable
        try:
            instance = playwright.chromium.launch(**options)
        except Exception:
            candidates = [Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Google/Chrome/Application/chrome.exe",
                          Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")) / "Microsoft/Edge/Application/msedge.exe"]
            found = next((p for p in candidates if p.is_file()), None)
            if not found or executable:
                raise ValueError("Chromium unavailable; run python -m playwright install chromium") from None
            instance = playwright.chromium.launch(**{**options, "executable_path": str(found)})
        token = _active_browser.set(instance)
        try:
            yield instance
        finally:
            _active_browser.reset(token)
            instance.close()


def asset_images(event: Event, input_root: Path | None = None, style: str | None = None) -> dict[str, str]:
    images = {}
    if style:
        images["campaign_art"] = campaign_art(event, style, input_root)[0]
        for ratio in event.assets.visual_variants:
            images['campaign_art_'+ratio] = campaign_art(event, style, input_root, ratio)[0]
    for name in ["logo", "hero_image", "speaker_photo", "qr_image"]:
        value = getattr(event.assets, name)
        if value:
            images["qr" if name == "qr_image" else name] = image_uri(value, input_root)
    scan_requested = event.qr_policy == "show" or (event.qr_policy == "auto" and any(
        word in (event.registration or '') + (event.poster_cta or '')
        for word in ['扫码', 'scan', 'Scan', 'QR']))
    if event.qr_policy == "hide":
        images.pop('qr', None)
    if event.registration_url and scan_requested and "qr" not in images:
        from ..security import valid_url
        if not valid_url(event.registration_url):
            raise ValueError("Cannot generate QR for an invalid URL")
        code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=4)
        code.add_data(event.registration_url)
        code.make(fit=True)
        buffer = io.BytesIO()
        code.make_image(fill_color="black", back_color="white").save(buffer, format="PNG")
        images["qr"] = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
    return images


def prepare(page, html: str, width: int, height: int) -> tuple[str, dict]:
    page.set_viewport_size({"width": width, "height": height})
    # Reject remote requests even if accidentally introduced in a future template.
    page.route("http://**/*", lambda route: route.abort())
    page.route("https://**/*", lambda route: route.abort())
    page.set_content(html, wait_until="load")
    page.evaluate("document.fonts.ready")
    measured = page.evaluate(FIT_SCRIPT)
    report = page.evaluate(CHECK_SCRIPT)
    report["font_sizes"] = measured
    report["font_families"] = page.locator("h1").evaluate("e=>getComputedStyle(e).fontFamily")
    report["browser_version"] = page.context.browser.version
    if page.locator('.poster').count():
        from ..validation import inspect_reading_pixels
        best = inspect_reading_pixels(page)
        if best['needs_visual_review']:
            def score(result):
                return sum(r['passing_fraction'] for r in result['regions'] if r['field'] in {'title','subtitle'})
            chosen = 'center'
            for alignment in ['flex-start','flex-end']:
                page.locator('.heading').evaluate('(e,a)=>e.style.justifyContent=a', alignment)
                trial = inspect_reading_pixels(page)
                if score(trial) > score(best):
                    best, chosen = trial, alignment
            page.locator('.heading').evaluate('(e,a)=>e.style.justifyContent=a', chosen)
            report = {**report, **page.evaluate(CHECK_SCRIPT)}
            best['heading_alignment'] = chosen
        report['image_readability'] = best
    session = page.context.new_cdp_session(page)
    try:
        session.send("DOM.enable")
        session.send("CSS.enable")
        document = session.send("DOM.getDocument")
        node = session.send("DOM.querySelector", {"nodeId": document["root"]["nodeId"], "selector": "h1"})
        report["actual_fonts"] = session.send("CSS.getPlatformFontsForNode", {"nodeId": node["nodeId"]})["fonts"]
    finally:
        session.detach()
    if not report["passed"]:
        raise ValueError("Layout validation failed: " + ", ".join(report["problems"]))
    return page.content(), report


def palette_for(event: Event, style: str, override: StyleOverride | None = None) -> list[str]:
    colors = event.brand.colors or (override.colors if override else [])
    return safe_palette(systems()[style]["palette"], colors, event.brand.forbidden_colors)


def render_preview(event: Event, style: str, destination: Path, *, instance=None, input_root=None) -> dict:
    destination.parent.mkdir(parents=True, exist_ok=True)
    palette = palette_for(event, style)
    images = asset_images(event, input_root, style)
    def generate(active):
        page = active.new_page()
        try:
            html, check = prepare(page, sheet_html(event, style, 1080, 1080, "square", palette, images, bool(issues(event))), 1080, 1080)
            page.screenshot(path=str(destination), animations="disabled")
            destination.with_suffix(".html").write_text(html, encoding="utf-8")
            return {"style_id": style, "event_digest": digest(event.model_dump()), "layout": check}
        finally:
            page.close()
    if instance:
        result = generate(instance)
    else:
        with browser() as active:
            result = generate(active)
    with Image.open(destination) as image:
        image.resize((540, 540), Image.Resampling.LANCZOS).save(destination)
    return result


def preview_document(event: Event, directory: Path, recommendations: list[dict]) -> None:
    cards = ''.join(f'<article><h2>{r["position"]}. {escape(profiles()[r["style_id"]]["name"])}</h2><img src="{escape(r["preview_path"])}"><p>{escape(r["reason"])}</p><p>取舍：{escape(r["tradeoff"])}</p></article>' for r in recommendations)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "recommendations.html").write_text(f'<!doctype html><html lang="zh"><meta charset="utf-8"><title>{escape(event.title)} · 风格推荐</title><style>body{{font:16px system-ui;margin:40px;background:#f3f1ec}}main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px}}article{{background:white;padding:24px;border:1px solid #ccc}}img{{width:100%}}h1{{font-size:32px}}</style><h1>{escape(event.title)} · 三选一</h1><p>选择 1/2/3、自动选最优，或换一批。规则分数仅用于排序。</p><p>风格预览复用原创示范素材；选定后将为本次活动创作专属主视觉。</p><main>{cards}</main></html>', encoding="utf-8")


def batch_render(
    event: Event, destination: Path, style: str, *, draft: bool = False,
    selection: dict | None = None, override: StyleOverride | None = None,
    input_root: Path | None = None, instance=None,
) -> dict:
    """One call produces the entire campaign. Reject incomplete facts unless visibly draft."""
    problems = issues(event)
    if problems and not draft:
        raise ValueError("Facts need confirmation:\n" + "\n".join(problems))
    style = resolve_style(override.base_style if override else style)
    ranking = rank(event)
    selected_score = next(s for s in ranking["style_scores"] if s["style_id"] == style)
    palette_conflict_repaired = bool(override and override.colors and selected_score["conflicts"] == ["preset palette uses a forbidden color"])
    if not selected_score["eligible"] and not palette_conflict_repaired:
        # Explicit branding recoloring can repair palette conflicts; forbidden style cannot be bypassed.
        raise ValueError("Style conflicts with hard brand constraints: " + ", ".join(selected_score["conflicts"]))
    palette = palette_for(event, style, override)
    images = asset_images(event, input_root, style)
    art_receipt = campaign_art(event, style, input_root)[1]
    form = invitation_format(event, style)
    iw, ih = INVITATION_SIZES[form]
    sizes = {**SIZES, "invitation": (iw, ih, "invitation")}
    destination = Path(destination).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and any(destination.iterdir()) and not (destination / "manifest.json").is_file():
        raise ValueError("Output directory is nonempty and is not an EventCraft campaign")
    with tempfile.TemporaryDirectory(prefix=".eventcraft-", dir=destination.parent) as temporary:
        stage = Path(temporary)
        persisted = event.model_copy(deep=True)
        if event.assets.visual_receipt:
            # Export a self-contained receipt/art pair rather than a machine-specific source path.
            (stage / "campaign_art.png").write_bytes(base64.b64decode(images["campaign_art"].split(",", 1)[1]))
            write_json(stage / "campaign_art_receipt.json", {**art_receipt, "image": "campaign_art.png"})
            persisted.assets.visual_receipt = "campaign_art_receipt.json"
        for ratio in event.assets.visual_variants:
            _, variant_receipt = campaign_art(event, style, input_root, ratio)
            name = 'campaign_art_'+ratio
            (stage/(name+'.png')).write_bytes(base64.b64decode(images[name].split(',',1)[1]))
            write_json(stage/(name+'_receipt.json'), {**variant_receipt,'image':name+'.png'})
            persisted.assets.visual_variants[ratio] = name+'_receipt.json'
        write_json(stage / "event.json", persisted.model_dump())
        if override:
            write_json(stage / "style_override.json", override.model_dump())
        copy = campaign(event)
        (stage / "copy").mkdir()
        for name, text in copy.items():
            if draft:
                text = "DRAFT / 草稿待确认\n" + text
            (stage / "copy" / name).write_text(text, encoding="utf-8")
        if images.get("qr"):
            (stage / "registration_qr.png").write_bytes(base64.b64decode(images["qr"].split(",", 1)[1]))
        checks = {}
        def generate(active):
            page = active.new_page()
            try:
                for name, (width, height, kind) in sizes.items():
                    html, check = prepare(page, sheet_html(event, style, width, height, kind, palette, images, draft), width, height)
                    page.screenshot(path=str(stage / (name + ".png")), animations="disabled")
                    (stage / (name + ".html")).write_text(html, encoding="utf-8")
                    for key in ["title", "when", "where"] + (["registration"] if kind == "invitation" else []):
                        if facts(event)[key] not in page.locator(".sheet").text_content():
                            raise ValueError(f"Rendered output missing key fact: {key}")
                    checks[name] = check
                    if name == "invitation":
                        # Exactly the same typeset artwork is exported as vector-text print stationery.
                        mm_width = 210 if form == "formal-card" else 297 if form == "folded" else 270
                        zoom = mm_width * 96 / 25.4 / width
                        page.add_style_tag(content=f"@media print{{.stationery{{zoom:{zoom}}}}}")
                        page.pdf(path=str(stage / "invitation_print.pdf"), width=f"{mm_width}mm",
                                 height=f"{mm_width * height / width}mm", print_background=True)
                        if form == "folded":
                            outside, outside_check = prepare(page, invitation_html(event, style, width, height,
                                palette, images, draft, form, "outside"), width, height)
                            (stage / "invitation_outside.html").write_text(outside, encoding="utf-8")
                            page.screenshot(path=str(stage / "invitation_outside.png"))
                            page.add_style_tag(content=f"@media print{{.stationery{{zoom:{zoom}}}}}")
                            page.pdf(path=str(stage / "invitation_outside.pdf"), width=f"{mm_width}mm",
                                     height=f"{mm_width * height / width}mm", print_background=True)
                            writer = PdfWriter()
                            writer.append(stage / "invitation_outside.pdf")
                            writer.append(stage / "invitation_print.pdf")
                            with (stage / "invitation_folded_print.pdf").open("wb") as stream:
                                writer.write(stream)
                            checks["invitation_outside"] = outside_check
                print_html, check = prepare(page, sheet_html(event, style, 1080, 1527, "print", palette, images, draft), 1080, 1527)
                (stage / "poster_print.html").write_text(print_html, encoding="utf-8")
                page.pdf(path=str(stage / "poster_print.pdf"), format="A4", print_background=True, prefer_css_page_size=True, margin={"top":"0", "bottom":"0", "left":"0", "right":"0"})
                checks["poster_print"] = check
                page.set_content(letter_html(event, palette, draft), wait_until="load")
                page.evaluate("document.fonts.ready")
                page.pdf(path=str(stage / "invite_letter.pdf"), format="A4", print_background=True, prefer_css_page_size=True)
                (stage / "invite_letter.html").write_text(page.content(), encoding="utf-8")
            finally:
                page.close()
        if instance:
            generate(instance)
        else:
            with browser() as active:
                generate(active)
        for name, (w, h, _) in sizes.items():
            with Image.open(stage / (name + ".png")) as im:
                if im.size != (w, h):
                    raise ValueError("Unexpected PNG dimensions")
        pdf_pages = {}
        pdf_names = ["poster_print.pdf", "invite_letter.pdf", "invitation_print.pdf"]
        if form == "folded":
            pdf_names += ["invitation_outside.pdf", "invitation_folded_print.pdf"]
        for name in pdf_names:
            reader = PdfReader(stage / name)
            if not reader.pages:
                raise ValueError("PDF contains no pages")
            pdf_pages[name] = len(reader.pages)
        if pdf_pages["poster_print.pdf"] != 1:
            raise ValueError("A4 poster unexpectedly spans multiple pages")
        previews = ''.join(f'<figure><img src="{name}.png" alt="{name}"><figcaption>{name} · {w}×{h}</figcaption></figure>' for name, (w, h, _) in sizes.items())
        copies = '<p><a href="invitation_print.pdf">视觉邀请函 / Print invitation PDF</a></p>'
        if form == "folded":
            copies += '<p><a href="invitation_outside.png">折页封面与封底</a> · <a href="invitation_folded_print.pdf">双页展开打印 PDF</a></p>'
        copies += ''.join(f'<details open><summary>{escape(name)}</summary><pre>{escape(text)}</pre></details>' for name, text in copy.items())
        (stage / "preview.html").write_text(f'<!doctype html><html lang="{event.language}"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{escape(event.title)}</title><style>body{{font:16px system-ui;margin:40px;background:#f5f3ee;color:#202421}}main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:20px}}figure{{margin:0}}img{{width:100%;height:540px;object-fit:contain;object-position:top;background:#e7e5df}}figcaption{{margin:12px 0}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;padding:20px;background:white}}a{{color:#264c74}}details{{margin:20px 0}}</style><h1>{escape(event.title)}</h1><p>{escape("DRAFT / 草稿待确认" if draft else "DEMO / 虚构活动" if event.demo else "")}</p><p>{escape(profiles()[style]["name"])} · {escape(event.language)}</p><main>{previews}</main><p><a href="poster_print.pdf">A4 海报 PDF</a> · <a href="invite_letter.pdf">正式邀请函 PDF</a> · <a href="event.json">活动数据</a> · <a href="manifest.json">检查记录</a></p>{copies}</html>', encoding="utf-8")
        records = []
        for file in sorted(stage.rglob("*")):
            if file.is_file():
                record = {"path": file.relative_to(stage).as_posix(), "bytes": file.stat().st_size,
                          "sha256": hashlib.sha256(file.read_bytes()).hexdigest()}
                if file.suffix == ".png":
                    with Image.open(file) as im:
                        record["dimensions"] = list(im.size)
                records.append(record)
        manifest = {
            "generator": "EventCraft visual system 2", "event_digest": digest(persisted.model_dump()),
            "source_event_digest": digest(event.model_dump()), "language": event.language,
            "style": "custom" if override else style, "base_style": style,
            "generation_mode": "event-specific-host-art" if event.assets.visual_receipt else "reusable-art-fallback", "draft": draft,
            "artwork": art_receipt, "composition": systems()[style]["layout"],
            "invitation_format": form,
            "publishable": not draft and not problems and not event.demo,
            "batch_entry_calls": 1, "files": records,
            "selection": selection or {**ranking, "selected_style": style, "selection_source": "reference" if override else "user-specified"},
            "checks": {"facts": not problems, "fact_issues": problems, "layouts": checks,
                       "png_dimensions": True, "pdf_pages": pdf_pages, "contrast": round(contrast(palette[0], palette[1]), 2),
                       "registration_url": "syntax-checked-only" if event.registration_url else "not-provided",
                       "qr": "user-image-preserved-unverified" if event.assets.qr_image and images.get('qr') else "generated-from-url" if images.get('qr') else "absent"},
            "palette": palette,
        }
        write_json(stage / "manifest.json", manifest)
        # Only replace verified, known generated files after the complete batch succeeds.
        destination.mkdir(parents=True, exist_ok=True)
        staged_files = [file for file in sorted(stage.rglob("*")) if file.is_file()]
        staged_names = {file.relative_to(stage).as_posix() for file in staged_files}
        obsolete_files = [destination / name for name in ["registration_qr.png", "style_override.json", "campaign_art.png", "campaign_art_receipt.json", "campaign_art_square.png", "campaign_art_square_receipt.json", "campaign_art_print.png", "campaign_art_print_receipt.json", "invitation_outside.png", "invitation_outside.html", "invitation_outside.pdf", "invitation_folded_print.pdf"]
                          if name not in staged_names and (destination / name).is_file()]
        for obsolete in obsolete_files:
            if not obsolete.resolve().is_relative_to(destination):
                raise ValueError("Obsolete artifact escapes campaign directory")
        for file in staged_files:
            target = destination / file.relative_to(stage)
            if not target.resolve().is_relative_to(destination):
                raise ValueError("Output path escapes campaign directory through a symbolic link")
        for file in staged_files:
            target = destination / file.relative_to(stage)
            target.parent.mkdir(parents=True, exist_ok=True)
            # Windows preview/indexing processes may briefly hold a completed artifact.
            # Keep the verified staged source and retry only transient sharing failures.
            for attempt in range(10):
                try:
                    os.replace(file, target)
                    break
                except PermissionError:
                    if os.name != "nt" or attempt == 9:
                        raise
                    time.sleep(0.2)
        # Remove only known obsolete optional artifacts; never delete unrelated user files.
        for obsolete in obsolete_files:
            obsolete.unlink()
        return manifest
