"""Real host assets -> public import/render pipeline; no reference-directory dependency."""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from eventcraft.extractors import extract
from eventcraft.renderer import batch_render, browser, palette_for, prepare
from eventcraft.renderer.campaigns import INVITATION_SIZES
from eventcraft.renderer.templates import sheet_html
from eventcraft.schema import Event
from eventcraft.security import write_json
from eventcraft.visuals import import_art, systems, visual_plan

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'assets/campaigns/visual-v3'
OUT = ROOT / 'examples/visual-v3'


def inputs():
    garden = Event(title='未来花园', subtitle='艺术与科技，共创绿色未来', category='exhibition',
                   start='2026-11-14T14:00', end='2026-11-14T17:00', timezone='Asia/Shanghai',
                   venue='虚构花园美术馆 · 主展厅', registration='无需报名',
                   audience=['designers', 'students'], formality='casual',
                   keywords=['植物', '生态艺术', '未来花园', '科技'],
                   style_description='以植物形态和未来生态花园为主题，不使用与主题无关的人脸、跑者或音乐人', demo=True)
    basketball = Event(title='城市篮球夜赛', subtitle='球场相遇，一起突破', category='sports', subtype='basketball',
                       start='2026-11-21T19:00', end='2026-11-21T21:00', timezone='Asia/Shanghai',
                       venue='虚构城市运动中心 · 篮球馆', registration='扫码报名',
                       registration_url='https://example.org/fictional/basketball', qr_policy='show',
                       keywords=['篮球', '夜赛', '竞技'], formality='casual', demo=True)
    return garden, basketball


def plan_all():
    garden, basketball = inputs()
    WORK.mkdir(parents=True, exist_ok=True)
    write_json(WORK / 'garden.json', garden.model_dump())
    write_json(WORK / 'basketball.json', basketball.model_dump())
    for sid in systems():
        write_json(WORK / (sid+'-plan.json'), visual_plan(garden, sid))
    write_json(WORK / 'basketball-plan.json', visual_plan(basketball, 'tech-gradient'))
    print('Eleven event-specific public art plans prepared')


def contact(paths, target, cols, size):
    sheet = Image.new('RGB', (cols*size[0], ((len(paths)+cols-1)//cols)*size[1]), '#e7e3da')
    draw = ImageDraw.Draw(sheet)
    for i, (label, path) in enumerate(paths):
        with Image.open(path) as source:
            thumb = ImageOps.contain(source.convert('RGB'), (size[0]-24, size[1]-50))
        x, y = i % cols * size[0], i // cols * size[1]
        draw.text((x+14, y+12), label, fill='#202421')
        sheet.paste(thumb, (x+(size[0]-thumb.width)//2, y+38))
    target.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(target)


def render():
    garden = extract(WORK / 'garden.json')
    basketball = extract(WORK / 'basketball.json')
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    with browser() as active:
        for sid in systems():
            event = garden.model_copy(deep=True)
            event.assets.visual_receipt = str(WORK / ('sports-paint' if sid == 'sports-dynamic' else sid) / 'receipt.json')
            if sid == 'tech-gradient':
                event.assets.visual_variants['square'] = str(WORK/'tech-square/receipt.json')
            manifest = batch_render(event, OUT / sid, sid, instance=active)
            results.append({'case': sid, 'mode': manifest['generation_mode'], 'checks': manifest['checks']})
        basketball.assets.visual_receipt = str(WORK / 'basketball/receipt.json')
        manifest = batch_render(basketball, OUT / 'basketball', 'tech-gradient', instance=active)
        results.append({'case': 'same-style-basketball', 'checks': manifest['checks']})
        for form in INVITATION_SIZES:
            sid = 'luxury-elegant' if form == 'formal-card' else 'retro-print' if form == 'ticket-stub' else 'editorial-minimal' if form == 'folded' else 'tech-gradient'
            event = garden.model_copy(deep=True)
            event.invitation_format = form
            # QR cases are separate facts: regenerate an import plan for the same artwork as user-art replay.
            event.assets.visual_receipt = str(WORK / sid / 'receipt.json')
            manifest = batch_render(event, OUT / 'invitations' / form, sid, instance=active)
            results.append({'case': form, 'checks': manifest['checks']})
        page = active.new_page()
        for name, title in {'short':'花园','long-zh':'面向未来城市公共空间的跨学科生态艺术与植物科技创新实践展览',
                            'english':'Future Gardens: Art, Ecology and Creative Technology',
                            'bilingual':'未来花园 Future Gardens：艺术与科技共创'}.items():
            event = garden.model_copy(deep=True)
            event.title = title
            event.language = 'en' if name == 'english' else 'bilingual' if name == 'bilingual' else 'zh'
            # Length stress tests reuse art explicitly; they are not new AI generation claims.
            from eventcraft.renderer import asset_images
            sid = 'tech-gradient'
            source_event = garden.model_copy(deep=True)
            source_event.assets.visual_receipt = str(WORK / sid / 'receipt.json')
            images = asset_images(source_event, style=sid)
            if name != 'short':
                # These are typography variations of one fictional exhibition, explicitly reused.
                from eventcraft.security import image_uri
                images['campaign_art'] = image_uri(WORK/'title-space/tech-gradient.png')
            for ratio, w, h in [('portrait',1080,1920),('square',1080,1080),('print',1080,1527)]:
                html, report = prepare(page, sheet_html(event,sid,w,h,ratio,palette_for(event,sid),images),w,h)
                target = OUT / 'titles'
                target.mkdir(exist_ok=True)
                page.screenshot(path=str(target/(name+'-'+ratio+'.png')))
                (target/(name+'-'+ratio+'.html')).write_text(html,encoding='utf-8')
                results.append({'case':'title-'+name+'-'+ratio,'checks':report,'art_mode':'explicit-reuse-for-typesetting-stress'})
        page.close()
    contact([(sid, OUT/sid/'poster_portrait.png') for sid in systems()],OUT/'style-gallery.png',5,(480,900))
    contact([(sid, OUT/sid/'poster_square.png') for sid in systems()],OUT/'square-gallery.png',5,(420,460))
    contact([(form, OUT/'invitations'/form/'invitation.png') for form in INVITATION_SIZES],OUT/'invitation-gallery.png',2,(900,800))
    contact([('Botanical exhibition',OUT/'tech-gradient/poster_portrait.png'),('Basketball night',OUT/'basketball/poster_portrait.png')],OUT/'dynamic-comparison.png',2,(540,1020))
    contact([(name,OUT/'titles'/(name+'-portrait.png')) for name in ['short','long-zh','english','bilingual']],OUT/'title-gallery.png',4,(400,770))
    cards = ''.join(f'<article><h2>{sid}</h2><a href="{sid}/preview.html"><img src="{sid}/poster_portrait.png"></a></article>' for sid in systems())
    invites = ''.join(f'<p><a href="invitations/{form}/preview.html">{form} · PNG / PDF</a></p>' for form in INVITATION_SIZES)
    (OUT/'index.html').write_text(f'<!doctype html><meta charset="utf-8"><title>EventCraft v3 · Fictional acceptance gallery</title><style>body{{background:#e7e3da;margin:40px;font:16px system-ui}}main{{display:grid;grid-template-columns:repeat(5,1fr);gap:24px}}img{{width:100%}}</style><h1>EventCraft v3 · 虚构测试活动</h1><p>十种艺术指导，针对本次活动分别实际调用内置 ImageGen。所有活动事实均为虚构。</p><main>{cards}</main>{invites}<p><a href="dynamic-comparison.png">同风格不同主题</a> · <a href="title-gallery.png">标题压力测试</a> · <a href="installed-runtime/preview.html">隔离 Skill 的深空论坛</a> · <a href="print-gallery.png">十风格 PDF 栅格总览</a> · <a href="print-invitation-gallery.png">邀请函 PDF 栅格总览</a></p>',encoding='utf-8')
    write_json(ROOT/'docs/acceptance-v3-layouts.json', results)
    print(f'Rendered {len(results)} cases through public renderer: {OUT}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action',choices=['plan','import','render'])
    parser.add_argument('--case')
    parser.add_argument('--image',type=Path)
    args = parser.parse_args()
    if args.action == 'plan':
        plan_all()
    elif args.action == 'import':
        import_art(WORK/(args.case+'-plan.json'),args.image,WORK/args.case,'codex-imagegen')
    else:
        render()
