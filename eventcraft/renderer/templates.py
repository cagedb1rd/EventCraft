"""Original code-native visual systems. All factual text is escaped HTML."""

import html
from importlib.resources import files

from ..copywriting import campaign
from ..recommendation import profiles
from ..schema import Event, facts
from ..validation import contrast


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def decoration(style: str, day: str) -> str:
    # Original vector ornaments. Day digits come from the actual event date.
    art = {
        "swiss-grid": '<circle cx="340" cy="270" r="215" fill="var(--accent)"/><path d="M70 490H620 M340 30V510" stroke="var(--fg)" stroke-width="4"/><circle cx="340" cy="270" r="95" fill="var(--bg)"/>',
        "editorial-minimal": '<rect x="120" y="20" width="380" height="480" fill="var(--accent)"/><path d="M120 500L500 20H120Z" fill="var(--fg)"/><circle cx="390" cy="210" r="105" fill="var(--bg)"/>',
        "tech-gradient": '<defs><radialGradient id="light"><stop stop-color="var(--accent)"/><stop offset="1" stop-color="var(--bg)" stop-opacity="0"/></radialGradient></defs><circle cx="320" cy="260" r="245" fill="url(#light)"/>' + ''.join(f'<ellipse cx="320" cy="260" rx="{210-i*30}" ry="{85-i*10}" transform="rotate({i*27-30} 320 260)" fill="none" stroke="var(--accent)" stroke-width="3" opacity=".8"/>' for i in range(5)),
        "academic-clean": ''.join(f'<rect x="{60+i*120}" y="{220-i*26}" width="85" height="{220+i*26}" rx="2" fill="var(--accent)" opacity="{.3+i*.14}"/>' for i in range(5)) + '<path d="M55 455H650M55 90V455" stroke="var(--fg)" stroke-width="3"/>',
        "neo-brutal": '<circle cx="340" cy="255" r="215" fill="var(--accent)" stroke="var(--fg)" stroke-width="12"/><path d="M340 80L370 210L510 190L410 270L485 390L350 325L270 440L275 300L130 275L285 240Z" fill="var(--bg)" stroke="var(--fg)" stroke-width="8"/>',
        "retro-print": '<path d="M145 500V230A200 200 0 0 1 545 230V500Z" fill="var(--accent)"/>' + ''.join(f'<path d="M{180+i*30} 500V250A{165-i*30} {165-i*30} 0 0 1 {510-i*30} 250V500" fill="none" stroke="var(--bg)" stroke-width="11"/>' for i in range(5)),
        "neon-night": '<path d="M120 490V205A220 220 0 0 1 560 205V490" fill="none" stroke="var(--accent)" stroke-width="10"/><path d="M170 490V205A170 170 0 0 1 510 205V490" fill="none" stroke="var(--fg)" stroke-width="2"/><path d="M70 490H610" stroke="var(--accent)" stroke-width="8"/>',
        "warm-playful": '<circle cx="480" cy="125" r="72" fill="var(--accent)" opacity=".55"/><path d="M335 485Q330 300 390 175M335 390Q200 290 150 350Q230 440 335 390M340 320Q430 210 540 310Q450 385 340 320" fill="var(--accent)" stroke="var(--fg)" stroke-width="5"/><path d="M160 480Q340 520 520 480" fill="none" stroke="var(--fg)" stroke-width="4"/><g fill="var(--bg)" stroke="var(--fg)" stroke-width="4"><ellipse cx="365" cy="155" rx="52" ry="90" transform="rotate(-45 365 155)"/><ellipse cx="405" cy="140" rx="52" ry="90" transform="rotate(35 405 140)"/><circle cx="380" cy="175" r="28" fill="var(--accent)"/></g>',
        "luxury-elegant": '<g fill="none" stroke="var(--accent)" stroke-width="2">' + ''.join(f'<ellipse cx="340" cy="260" rx="{105+i*8}" ry="{210-i*6}" transform="rotate({i*30} 340 260)"/>' for i in range(6)) + '<circle cx="340" cy="260" r="105"/></g>',
        "sports-dynamic": '<path d="M-50 410L720 50V175L-50 535Z" fill="var(--accent)"/>' + ''.join(f'<path d="M-20 {100+i*42}L680 {i*42-180}" stroke="var(--accent)" stroke-width="8" opacity=".45"/>' for i in range(7)) + f'<text x="620" y="390" text-anchor="end" font-size="340" font-weight="900" fill="var(--fg)" opacity=".2">{escape(day)}</text>',
    }
    return '<svg aria-hidden="true" viewBox="0 0 680 540" xmlns="http://www.w3.org/2000/svg">' + art[style] + '</svg>'


def sheet_html(
    event: Event, style: str, width: int, height: int, kind: str, palette: list[str],
    images: dict[str, str], draft: bool = False,
) -> str:
    f = facts(event)
    profile = profiles()[style]
    en = event.language == "en"
    invite = kind == "invitation"
    square = kind == "square"
    day = event.start[8:10] if event.start else ""
    date = event.start[:10].replace("-", ".") if event.start else ("PENDING" if en else "待确认")
    eyebrow = "INVITATION" if invite else event.category.upper().replace("-", " ")
    headline = f['title']
    labels = {"when": "DATE / TIME", "where": "LOCATION", "registration": "REGISTRATION", "fee": "ADMISSION"} if en else {"when": "日期 / 时间", "where": "活动地点", "registration": "报名方式", "fee": "参与费用"}
    details = ''.join(f'<div class="fact" data-field="{key}"><span>{labels[key]}</span><p data-fit="24">{escape(f[key])}</p></div>' for key in ["when", "where", "registration", "fee"] if f[key])
    if event.deadline:
        details += f'<div class="fact" data-field="deadline"><span>{"DEADLINE" if en else "报名截止"}</span><p data-fit="22">{escape(event.deadline)}</p></div>'
    logo = f'<img class="logo" src="{images["logo"]}" alt="User logo">' if images.get("logo") else ''
    photos = ''.join(f'<img class="{key}" src="{images[key]}" alt="User {key}" data-asset="{key}">' for key in ["hero_image", "speaker_photo"] if images.get(key))
    qr = f'<div class="qr"><img src="{images["qr"]}" alt="Registration QR"><span>{"REGISTER" if en else "扫码报名"}</span></div>' if images.get("qr") else ''
    bullet_items = event.teams or event.highlights[:3]
    bullets = ''.join(f'<li>{escape(v)}</li>' for v in bullet_items)
    speaker = ("Speakers · " if en else "主讲人 · ") + " / ".join(event.speakers[:3]) if event.speakers else ''
    greeting = (event.recipient or ("Dear guest" if en else "诚邀莅临")) if invite else ''
    status = "DRAFT · NOT FOR PUBLICATION / 草稿待确认" if draft else "DEMO · FICTIONAL EVENT / 虚构活动" if event.demo else ''
    css = files("eventcraft").joinpath("data/styles.css").read_text(encoding="utf-8")
    label = palette[2] if contrast(palette[0], palette[2]) >= 4.5 else palette[1]
    vars_css = f"--bg:{palette[0]};--fg:{palette[1]};--accent:{palette[2]};--label:{label};--w:{width}px;--h:{height}px"
    title_min = 56 if kind == "portrait" else 44 if kind in {"invitation", "print"} else 40
    body = f'''<article class="sheet {style} {kind}" style="{vars_css}" data-style="{style}">
<div class="status">{escape(status)}</div>
<header><div class="edition">{escape(eyebrow)}</div><div class="date-index">{escape(date)}</div>{logo}</header>
<section class="heading"><div class="greeting">{escape(greeting)}</div><h1 data-fit="{title_min}" data-field="title">{escape(headline)}</h1><p class="subtitle" data-fit="22">{escape(event.subtitle)}</p></section>
<section class="visual">{decoration(style, day)}{photos}</section>
<section class="summary"><ul data-fit="22">{bullets}</ul><p class="speakers" data-fit="22">{escape(speaker)}</p></section>
<section class="details">{details}</section>
<footer><div class="credit" data-fit="18">{escape(event.organizer or '')}</div>{qr}<span class="series">{escape('YOU ARE INVITED' if en and invite else 'EVENT / ' + date if en else '邀请函' if invite else '活动 / ' + date)}</span></footer>
</article>'''
    # Attribute identifies intent; print layout is adapted independently of screenshot sizes.
    del square, profile
    return f'''<!doctype html><html lang="{'en' if en else 'zh-CN'}"><head><meta charset="utf-8"><meta name="viewport" content="width={width}"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; font-src data:;"><title>{escape(event.title)}</title><style>{css}</style></head><body>{body}</body></html>'''


def letter_html(event: Event, palette: list[str], draft: bool = False) -> str:
    text = campaign(event)["invitation.txt"]
    lines = ''.join(f'<p>{escape(line) or "&nbsp;"}</p>' for line in text.splitlines())
    status = "DRAFT / 草稿待确认" if draft else "DEMO / 虚构活动" if event.demo else ''
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>{escape(event.title)}</title><style>
@page{{size:A4;margin:22mm}}body{{font-family:"Microsoft YaHei","Noto Sans CJK SC","PingFang SC",sans-serif;color:{palette[1]};background:{palette[0]};font-size:14px;line-height:1.9}}h1{{font-family:"SimSun","Noto Serif CJK SC",serif;font-size:32px;font-weight:400;border-bottom:1px solid {palette[2]};padding-bottom:24px;overflow-wrap:anywhere}}p{{margin:6px 0;overflow-wrap:anywhere}}.status{{color:{palette[2]};font-size:11px;letter-spacing:2px}}.letter{{border-top:5px solid {palette[2]};padding-top:24px}}</style></head><body><div class="letter"><div class="status">{escape(status)}</div><h1>{escape('Invitation' if event.language=='en' else '正式邀请函')}</h1>{lines}</div></body></html>'''
