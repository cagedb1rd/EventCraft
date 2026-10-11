"""Meaningful runtime contracts for semantics, typography, optional QR and quiet layouts."""
import json
from pathlib import Path

import pytest

from eventcraft.composition import composition
from eventcraft.extractors import extract, parse_text
from eventcraft.renderer import asset_images, batch_render
from eventcraft.schema import facts, issues
from eventcraft.security import write_json
from eventcraft.typography import typography
from eventcraft.visuals import campaign_art, import_art, systems, visual_plan

ROOT = Path(__file__).resolve().parents[1]


def test_same_style_new_event_changes_semantic_brief_and_title_space(event):
    first = visual_plan(event, 'tech-gradient')
    other = event.model_copy(deep=True)
    other.title = '城市篮球夜赛'
    other.category = 'sports'
    other.subtype = 'basketball'
    other.keywords = ['篮球', '夜赛']
    second = visual_plan(other, 'tech-gradient')
    assert first['prompt'] != second['prompt']
    assert other.title in second['prompt'] and 'basketball' in second['prompt']
    assert first['event_digest'] != second['event_digest']
    event.title = '面向未来城市公共空间的跨学科生态艺术与植物科技创新实践展览'
    assert composition(event,'tech-gradient')['zones']['title'][3] > first['composition']['zones']['title'][3]
    assert 'image/' not in second['prompt']


def test_ten_complete_font_contracts_have_distinct_chinese_voices():
    voices = set()
    for sid in systems():
        t = typography(sid)
        assert all(t[k] for k in ['zh_title','en_title','subtitle','information','numbers',
                                 'scale','line_break','bilingual','long_title'])
        voices.add((t['zh_title'][0],t['weight'],t['shape'],t['tracking']))
    assert len(voices) == 10


def test_natural_dates_and_explicit_timezone(event):
    assert 'Asia/Shanghai' not in facts(event)['when']
    assert 'T14:' not in facts(event)['when']
    event.language = 'en'
    assert facts(event)['when'].startswith('OCT 26, 2026')
    event.show_timezone = True
    event.timezone_label = 'China Standard Time'
    assert 'China Standard Time' in facts(event)['when']


def test_qr_requires_scan_intent_and_missing_link_is_actionable(event):
    assert 'qr' not in asset_images(event)
    event.registration = '请扫码报名'
    assert 'qr' in asset_images(event)
    event.qr_policy = 'hide'
    assert 'qr' not in asset_images(event)
    event.qr_policy = 'show'
    event.registration_url = None
    assert any('QR requested' in s for s in issues(event))


def test_timezone_text_does_not_become_an_ai_theme():
    event = parse_text('活动名称：深空计算论坛\n时区：Asia/Shanghai')
    assert 'AI' not in event.keywords
    assert 'AI' in parse_text('活动名称：校园AI分享会').keywords


@pytest.mark.render
def test_ratio_asset_relocates_and_replays_without_local_references(event, chromium, tmp_path):
    plan = tmp_path/'plan.json'
    source = ROOT/'eventcraft/data/art/tech-gradient.png'
    write_json(plan, visual_plan(event,'tech-gradient'))
    import_art(plan,source,tmp_path/'portrait','codex-imagegen')
    write_json(plan, visual_plan(event,'tech-gradient','square'))
    import_art(plan,source,tmp_path/'square','codex-imagegen')
    event.assets.visual_receipt = str(tmp_path/'portrait/receipt.json')
    event.assets.visual_variants['square'] = str(tmp_path/'square/receipt.json')
    output = tmp_path/'campaign'
    batch_render(event,output,'tech-gradient',instance=chromium)
    exported = extract(output/'event.json')
    assert exported.assets.visual_variants['square'] == str((output/'campaign_art_square_receipt.json').resolve())
    assert campaign_art(exported,'tech-gradient',ratio='square')[1]['composition']['ratio'] == 'square'
    html = (output/'poster_square.html').read_text(encoding='utf-8')
    assert 'ratio-art' in html and 'data:image/' in html
    assert 'Asia/Shanghai' not in html
    manifest = json.loads((output/'manifest.json').read_text(encoding='utf-8'))
    assert manifest['generation_mode'] == 'event-specific-host-art'
    assert manifest['checks']['qr'] == 'absent'
    exported.assets.visual_variants['square'] = exported.assets.visual_receipt
    with pytest.raises(ValueError,match='ratio mismatch'):
        campaign_art(exported,'tech-gradient',ratio='square')
