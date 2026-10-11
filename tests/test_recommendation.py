from pathlib import Path

import pytest

from eventcraft.extractors import extract
from eventcraft.recommendation import profiles, rank, shortlist
from eventcraft.recommendation.state import choose, save_recommendations
from eventcraft.schema import Event


@pytest.mark.parametrize("category,title,formality,expected", [
    ("lecture", "校园 AI Agent 分享", "professional", "tech-gradient"),
    ("academic", "学术研究论坛", "professional", "academic-clean"),
    ("wedding", "婚礼", "ceremonial", "luxury-elegant"),
    ("dinner", "高管闭门晚宴", "ceremonial", "luxury-elegant"),
    ("sports", "足球比赛", "casual", "sports-dynamic"),
    ("night-party", "DJ 夜间音乐派对", "casual", "neon-night"),
    ("esports", "电竞竞技比赛", "casual", "sports-dynamic"),
    ("market", "校园创意市集", "casual", "neo-brutal"),
    ("launch", "AI 科技新品发布", "professional", "tech-gradient"),
])
def test_scenarios(category, title, formality, expected):
    event = Event(title=title, category=category, formality=formality,
                  start="2026-11-20T19:00" if category == "night-party" else "2026-11-20T10:00")
    result = shortlist(rank(event))
    assert expected in [r["style_id"] for r in result]
    if category in {"sports", "wedding", "dinner", "esports"}:
        assert result[0]["style_id"] == expected
    assert all(r["style_id"] in profiles() for r in result)


def test_competition_and_party_differ():
    e = Event(title="电竞比赛", category="esports", formality="casual", start="2026-10-26T19:00")
    assert shortlist(rank(e))[0]["style_id"] == "sports-dynamic"
    e.title = "夜间电竞派对 DJ"
    assert shortlist(rank(e))[0]["style_id"] == "neon-night"


def test_determinism_and_no_missing_facts(event):
    assert rank(event) == rank(event)
    empty = Event(title="未知活动")
    for s in shortlist(rank(empty)):
        assert "学生" not in s["reason"] and "夜间" not in s["reason"]
    assert len({s["family"] for s in shortlist(rank(event))}) == 3


def test_brand_density_bilingual_constraints(event):
    event.brand.forbidden_styles = ["tech-gradient"]
    forbidden = profiles()["swiss-grid"]["palette"][0]
    event.brand.forbidden_colors = [forbidden]
    event.brand.high_contrast = True
    event.title *= 10
    event.language = "bilingual"
    ranking = rank(event)
    choices = shortlist(ranking)
    assert not {"tech-gradient", "swiss-grid"} & {s["style_id"] for s in choices}
    assert any(s["components"]["density"] < 10 for s in ranking["style_scores"])
    event.brand.colors = [forbidden]
    assert shortlist(rank(event)) == []
    with pytest.raises(ValueError):
        rank(event, {"type": 100})


def test_state_pagination_choices_and_stale_event(event, tmp_path):
    state = save_recommendations(event, tmp_path)
    chosen, stored = choose(event, tmp_path, "2")
    assert chosen == state["recommendations"][1]["style_id"]
    assert stored["selection_source"] == "three-choice"
    first = {s["style_id"] for s in state["recommendations"]}
    second = save_recommendations(event, tmp_path, 2)
    assert not first & {s["style_id"] for s in second["recommendations"]}
    assert choose(event, tmp_path, "自动选最优")[0] == state["style_scores"][0]["style_id"]
    assert choose(event, tmp_path, "复古印刷风")[0] == "retro-print"
    event.title = "Changed"
    with pytest.raises(ValueError, match="changed"):
        choose(event, tmp_path, "1")


def test_fourth_page_and_unknown(tmp_path):
    event = Event(title="general")
    state = save_recommendations(event, tmp_path, 4)
    assert len(state["recommendations"]) == 1
    with pytest.raises(ValueError):
        choose(event, tmp_path, "2")
    with pytest.raises(ValueError):
        choose(event, tmp_path, "imaginary-style")


def test_sample_types_exist():
    root = Path(__file__).resolve().parents[1]
    for path in (root / "examples/inputs").glob("*.json"):
        assert shortlist(rank(extract(path)))
