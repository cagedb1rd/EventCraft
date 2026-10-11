"""Ten art-directed compositions and four real stationery formats."""
import hashlib
import re
from importlib.resources import files

from ..composition import composition_css
from ..schema import Event, facts
from ..typography import typography_css
from ..visuals import systems
from .templates import escape

INVITATION_SIZES = {"boarding-pass": (1600, 800), "ticket-stub": (1600, 700),
                    "formal-card": (1080, 1350), "folded": (1800, 1000)}


def invitation_format(event: Event, style: str) -> str:
    if event.invitation_format != "auto":
        return event.invitation_format
    if event.formality == "ceremonial" or event.category in {"wedding", "dinner", "awards"}:
        return "formal-card"
    if event.category in {"conference", "tech", "launch", "forum"} or style == "tech-gradient":
        return "boarding-pass"
    if event.category in {"sports", "night-party", "esports", "market"} or style in {"retro-print", "neo-brutal", "neon-night", "sports-dynamic"}:
        return "ticket-stub"
    if event.category in {"exhibition", "workshop", "community"}:
        return "folded"
    return "formal-card"


def document(event: Event, body: str, width: int, css: str) -> str:
    return f'''<!doctype html><html lang="{'en' if event.language == 'en' else 'zh-CN'}"><head>
<meta charset="utf-8"><meta name="viewport" content="width={width}">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; font-src data:;">
<title>{escape(event.title)}</title><style>{css}</style></head><body>{body}</body></html>'''


def components(event: Event, images: dict, draft: bool) -> dict:
    f = facts(event)
    en = event.language == "en"
    labels = ["DATE / TIME", "LOCATION", "REGISTRATION", "ADMISSION", "RSVP BY"] if en else ["日期 / 时间", "活动地点", "报名方式", "参与费用", "报名截止"]
    details = ''.join(f'<div class="fact" data-field="{key}"><span>{label}</span><p data-fit="20">{escape(value)}</p></div>'
                      for key, label, value in zip(["when", "where", "registration", "fee", "deadline"], labels,
                                                  [f["when"], f["where"], f["registration"], f["fee"], f['deadline']]) if value)
    qr = f'<div class="qr"><img src="{images["qr"]}" alt="Registration QR"><span>{"REGISTER" if en else "扫码报名"}</span></div>' if images.get("qr") else ''
    logo = f'<img class="logo" src="{images["logo"]}" alt="User logo">' if images.get("logo") else ''
    art = f'<img class="campaign-art" src="{images["campaign_art"]}" alt="Original campaign artwork">' if images.get("campaign_art") else ''
    user = ''.join(f'<img class="{name}" data-asset="{name}" src="{images[name]}" alt="User {name}">'
                   for name in ["hero_image", "speaker_photo"] if images.get(name))
    return {"details": details, "qr": qr, "logo": logo, "art": art, "user": user,
            "date": event.start[:10].replace("-", ".") if event.start else "PENDING / 待确认",
            "status": "DRAFT / 草稿待确认" if draft else "DEMO / 虚构活动" if event.demo else "",
            "bullets": ''.join(f'<li>{escape(item)}</li>' for item in (event.teams or event.highlights[:3])),
            "speaker": (("Speakers / " if en else "主讲人 / ") + " · ".join(event.speakers[:3])) if event.speakers else ""}


def poster_html(event: Event, style: str, width: int, height: int, kind: str,
                palette: list[str], images: dict, draft=False) -> str:
    images = dict(images)
    variant = images.get('campaign_art_'+kind)
    if variant:
        images['campaign_art'] = variant
    c = components(event, images, draft)
    css = files("eventcraft").joinpath("data/campaigns.css").read_text(encoding="utf-8")
    f = facts(event)
    en = event.language == "en"
    core_details = ''.join(f'<div class="fact" data-field="{key}"><span>{label}</span><p data-fit="22">{escape(f[key])}</p></div>'
                           for key, label in [("when", "DATE / TIME" if en else "日期 / 时间"),
                                              ("where", "LOCATION" if en else "活动地点")])
    cta = event.poster_cta or (("Scan to Register" if en else "扫码报名") if images.get('qr') else '')
    # Posters intentionally omit full registration URLs, fees, deadlines, bullets and speaker lists.
    qr = f'<div class="qr"><img src="{images["qr"]}" alt="Registration QR"></div>' if images.get("qr") else ''
    fonts = typography_css(style)
    # A long introduction is not a poster slogan. Preserve it fully in invitation/copy.
    subtitle_limit = 120 if event.language == 'en' else 60 if event.language == 'bilingual' else 40
    poster_subtitle = event.subtitle if len(event.subtitle) <= subtitle_limit and '\n' not in event.subtitle else ''
    language_class = "latin-title" if not re.search(r"[\u4e00-\u9fff]", event.title) else "cjk-title"
    language_class += ' ratio-art' if variant else ' portrait-art'
    language_class += ' has-qr' if images.get('qr') else ''
    body = f'''<article class="sheet poster {style} {kind} {language_class}" data-style="{style}" data-composition="{systems()[style]['layout']}"
style="--bg:{palette[0]};--fg:{palette[1]};--accent:{palette[2]};--w:{width}px;--h:{height}px">
<div class="art-backdrop">{c['art']}</div><div class="status">{c['status']}</div>
<header>{c['logo']}</header>
<section class="heading" data-readability-zone="title"><h1 data-fit="40" data-field="title">{escape(event.title)}</h1><p class="subtitle" data-fit="22">{escape(poster_subtitle)}</p></section>
<section class="visual">{c['user']}</section><section class="summary" aria-hidden="true"></section>
<section class="details" data-readability-zone="facts">{core_details}</section><footer data-readability-zone="cta"><div class="footer-copy"><p class="cta" data-fit="22" data-field="cta">{escape(cta)}</p><div class="credit" data-fit="18">{escape(event.organizer or '')}</div></div>{qr}</footer></article>'''
    return document(event, body, width, css+fonts+composition_css(event, style, kind))


def invitation_html(event: Event, style: str, width: int, height: int, palette: list[str],
                    images: dict, draft=False, form: str | None = None, side="inside") -> str:
    form = form or invitation_format(event, style)
    c = components(event, images, draft)
    en = event.language == "en"
    number = hashlib.sha256((event.title + (event.start or "")).encode()).hexdigest()[:8].upper()
    serial = f"DESIGN / {number}" if en else f"设计编号 / {number}"
    disclaimer = "DESIGN ONLY · NOT AN ADMISSION CREDENTIAL" if en else "视觉邀请函 · 非实际入场凭证"
    greeting = event.recipient or ("You are invited" if en else "诚邀莅临")
    title = f'<h1 data-fit="36" data-field="title">{escape(event.title)}</h1>'
    qr = c['qr']
    stub = f'<aside class="stub"><div class="edition">{escape("GUEST COPY" if en else "来宾副券")}</div><div class="stub-art">{c["art"]}</div>{qr}<p class="serial">{serial}</p><p class="credential-note">{disclaimer}</p></aside>'
    main = f'<div class="invite-main"><header><div class="edition">{escape(form.replace("-", " ").upper())}</div>{c["logo"]}</header><section class="heading"><div class="greeting">{escape(greeting)}</div>{title}<p class="subtitle" data-fit="20">{escape(event.subtitle)}</p></section><section class="details">{c["details"]}</section><footer><div class="credit" data-fit="18">{escape(event.organizer or "")}</div><p class="serial">{serial}</p></footer></div>'
    if form in {"boarding-pass", "ticket-stub"}:
        content = f'<div class="pass-band">{c["art"]}<span>{escape("EVENT INVITATION" if en else "活动邀请函")}</span></div>{main}{stub}<div class="perforation"></div>'
    elif form == "formal-card":
        content = f'<div class="formal-art">{c["art"]}</div><div class="formal-frame"></div>{main}<div class="formal-qr">{qr}</div>'
    else:
        if side == "outside":
            content = f'<div class="fold-panel back"><div class="greeting">{escape(event.organizer or "")}</div><p>{escape(disclaimer)}</p>{qr}</div><div class="fold-panel cover"><div class="fold-art">{c["art"]}</div><div class="edition">{escape(greeting)}</div>{title}<p>{escape(event.subtitle)}</p></div>'
        else:
            content = f'<div class="fold-panel inner-art"><div class="fold-art">{c["art"]}</div><div class="edition">{escape(greeting)}</div>{title}<p class="subtitle" data-fit="20">{escape(event.subtitle)}</p></div><div class="fold-panel inner-info"><header><div class="edition">{escape("EVENT DETAILS" if en else "活动详情")}</div>{c["logo"]}</header><section class="details">{c["details"]}</section><ul>{c["bullets"]}</ul><footer><div class="credit">{escape(event.organizer or "")}</div>{qr}</footer></div>'
        content += '<div class="fold-line"></div><div class="fold-label">FOLD / 折线</div>'
    css = files("eventcraft").joinpath("data/invitations.css").read_text(encoding="utf-8")
    body = f'<article class="sheet stationery {form} {style}" data-invitation-format="{form}" style="--bg:{palette[0]};--fg:{palette[1]};--accent:{palette[2]};--w:{width}px;--h:{height}px"><div class="status">{c["status"]}</div>{content}</article>'
    return document(event, body, width, css+typography_css(style))
