"""Escaped factual typesetting routed to art-directed campaign compositions."""
import html

from ..copywriting import campaign
from ..schema import Event


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)

def sheet_html(event, style, width, height, kind, palette, images, draft=False):
    from .campaigns import invitation_html, poster_html
    if kind == "invitation":
        return invitation_html(event, style, width, height, palette, images, draft)
    return poster_html(event, style, width, height, kind, palette, images, draft)


def letter_html(event: Event, palette: list[str], draft: bool = False) -> str:
    text = campaign(event)["invitation.txt"]
    lines = ''.join(f'<p>{escape(line) or "&nbsp;"}</p>' for line in text.splitlines())
    status = "DRAFT / 草稿待确认" if draft else "DEMO / 虚构活动" if event.demo else ''
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>{escape(event.title)}</title><style>
@page{{size:A4;margin:22mm}}body{{font-family:"Microsoft YaHei","Noto Sans CJK SC","PingFang SC",sans-serif;color:{palette[1]};background:{palette[0]};font-size:14px;line-height:1.9}}h1{{font-family:"SimSun","Noto Serif CJK SC",serif;font-size:32px;font-weight:400;border-bottom:1px solid {palette[2]};padding-bottom:24px;overflow-wrap:anywhere}}p{{margin:6px 0;overflow-wrap:anywhere}}.status{{color:{palette[2]};font-size:11px;letter-spacing:2px}}.letter{{border-top:5px solid {palette[2]};padding-top:24px}}</style></head><body><div class="letter"><div class="status">{escape(status)}</div><h1>{escape('Invitation' if event.language=='en' else '正式邀请函')}</h1>{lines}</div></body></html>'''
