"""Stable, explainable ranking with hard constraints before weighted scoring."""

import json
from datetime import datetime
from functools import lru_cache
from importlib.resources import files

from ..schema import Event
from ..security import digest

AUDIENCE_ALIASES = {
    "学生": "students", "大学生": "students", "开发者": "developers", "研究者": "researchers",
    "亲友": "friends", "家庭": "families", "高管": "executives", "运动员": "athletes", "玩家": "gamers",
    "设计师": "designers", "来宾": "guests", "儿童": "children", "专业人士": "professionals",
}


@lru_cache
def catalog() -> dict:
    return json.loads(files("eventcraft").joinpath("data/style-profiles.json").read_text(encoding="utf-8"))


def profiles() -> dict:
    return catalog()["styles"]


def resolve_style(value: str) -> str:
    for sid, p in profiles().items():
        if value in {sid, p["name"], p["name_en"]}:
            return sid
    raise ValueError("Unknown style; use eventcraft gallery or a documented style ID")


def rank(event: Event, weights: dict | None = None) -> dict:
    weights = weights or catalog()["weights"]
    if set(weights) != set(catalog()["weights"]) or any(v < 0 for v in weights.values()) or sum(weights.values()) != 100:
        raise ValueError("Ranking weights must use seven documented dimensions and total 100")
    text = " ".join([event.title, event.subtitle, event.subtype, *event.keywords, *event.atmosphere]).lower()
    audience = [AUDIENCE_ALIASES.get(v, v.lower()) for v in event.audience]
    hour = datetime.fromisoformat(event.start).hour if event.start else None
    scene = "night" if hour is not None and (hour >= 18 or hour < 6) else "day" if hour is not None else "unknown"
    density = len(event.title) + len(event.subtitle) + sum(len(h) for h in event.highlights)
    scores = []
    for index, (sid, profile) in enumerate(profiles().items()):
        conflicts = []
        if sid in event.brand.forbidden_styles:
            conflicts.append("style explicitly forbidden")
        palette = [c.lower() for c in profile["palette"]]
        if any(c in event.brand.forbidden_colors for c in event.brand.colors):
            conflicts.append("required brand color is also forbidden")
        if not event.brand.colors and any(c in event.brand.forbidden_colors for c in palette):
            conflicts.append("preset palette uses a forbidden color")
        type_match = 1 if event.category in profile["types"] else 0.45 if event.category == "general" else 0.12
        # Distinguish an esports competition from a night entertainment event.
        if event.category == "esports":
            if sid == "sports-dynamic":
                type_match = 0.85 if any(k in text for k in ["party", "派对", "DJ".lower()]) else 1.0
            elif sid == "neon-night":
                type_match = 1.0 if any(k in text for k in ["party", "派对", "dj"]) else 0.42
        aud = max([1 if a in profile["audience"] else 0.35 for a in audience], default=0.5)
        if event.channels:
            aud = min(1, aud + (0.05 if profile["density"] != "high" and any(c in {"social", "社媒"} for c in event.channels) else 0))
        formal = 0.6 if event.formality == "unknown" else 1 if event.formality in profile["formality"] else 0.15
        if event.formality in profile["avoid"]:
            formal = 0
        keyword = any(k.lower() in text for k in profile["keywords"])
        scene_match = 0.5 if scene == "unknown" else 1 if profile["time"] in {"any", scene} else 0.25
        scene_score = min(1, scene_match * 0.45 + (0.55 if keyword else 0.25))
        if event.venue_mode == "outdoor" and sid in {"sports-dynamic", "warm-playful"}:
            scene_score = min(1, scene_score + 0.1)
        if event.assets.hero_image and profile["family"] in {"editorial", "space", "diagonal"}:
            scene_score = min(1, scene_score + 0.1)
        density_score = 1 if density < 120 else {"low": 0.25, "medium": 0.65, "high": 1}[profile["density"]]
        if len(event.title) > 80:
            density_score *= 0.65 if profile["density"] == "low" else 0.85
        parts = {
            "type": type_match, "audience": aud, "formality": formal, "scene": scene_score,
            "density": density_score, "brand": 1 if not event.brand.colors else 0.9,
            "readability": 1 if event.language in profile["language"] else 0,
        }
        score = round(sum(weights[k] * v for k, v in parts.items()), 2)
        cited = [f"活动「{event.title}」"] if event.title else []
        if event.category != "general":
            cited.append(f"类型 {event.category}")
        if event.audience:
            cited.append("面向 " + "、".join(event.audience))
        if event.formality != "unknown":
            cited.append("气质 " + event.formality)
        if keyword:
            found = next(k for k in profile["keywords"] if k.lower() in text)
            cited.append(f"主题含 {found}")
        if scene != "unknown":
            cited.append("夜间时段" if scene == "night" else "日间时段")
        reason = "；".join(cited or ["现有信息有限，采用通用适配"]) + "。采用" + profile["layout"]["poster"] + "。"
        scores.append({"style_id": sid, "score": score, "eligible": not conflicts, "conflicts": conflicts,
                       "components": {k: round(v * weights[k], 2) for k, v in parts.items()},
                       "reason": reason, "tradeoff": profile["tradeoff"], "preview_path": None,
                       "family": profile["family"], "_order": index})
    scores.sort(key=lambda s: (not s["eligible"], -s["score"], s["_order"]))
    for s in scores:
        s.pop("_order")
    return {
        "ranking_version": catalog()["ranking_version"], "weights": weights,
        "input_digest": digest(event.model_dump()), "profile_digest": digest(catalog()),
        "input_summary": {"category": event.category, "language": event.language, "title_length": len(event.title),
                          "audience": event.audience, "formality": event.formality, "scene": scene, "density": density},
        "style_scores": scores,
    }


def shortlist(ranking: dict, page: int = 1) -> list[dict]:
    if page < 1:
        raise ValueError("Recommendation page starts at 1")
    # All ten authored families are structurally distinct; ties preserve catalog order.
    eligible = [s for s in ranking["style_scores"] if s["eligible"]]
    result = []
    for offset, item in enumerate(eligible[(page - 1) * 3:page * 3]):
        result.append({**item, "rank": (page - 1) * 3 + offset + 1,
                       "position": offset + 1, "role": ["最适合", "稳妥替代", "更有创意"][offset]})
    return result
