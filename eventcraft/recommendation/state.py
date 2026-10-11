"""Cross-turn state guards against choosing a stale event or recommendation page."""

import json
from pathlib import Path

from ..schema import Event
from ..security import digest, write_json
from . import rank, resolve_style, shortlist


def save_recommendations(event: Event, directory: Path, page: int = 1, ranking: dict | None = None) -> dict:
    ranking = ranking or rank(event)
    state = {**ranking, "event_digest": digest(event.model_dump()), "page": page,
             "recommendations": shortlist(ranking, page), "selected_style": None, "selection_source": None}
    previous = directory / "state.json"
    history = []
    if previous.exists():
        saved = json.loads(previous.read_text(encoding="utf-8"))
        if saved.get("event_digest") == state["event_digest"]:
            history = saved.get("pages_seen", [])
    state["pages_seen"] = list(dict.fromkeys([*history, page]))
    write_json(directory / "state.json", state)
    write_json(directory / "recommendations.json", state)
    return state


def choose(event: Event, directory: Path, value: str) -> tuple[str, dict]:
    path = directory / "state.json"
    if not path.exists():
        raise ValueError("No saved recommendations; run recommend first")
    state = json.loads(path.read_text(encoding="utf-8"))
    if state["event_digest"] != digest(event.model_dump()):
        raise ValueError("Event changed; regenerate recommendations before choosing")
    value = value.strip().removeprefix("选 ").removeprefix("选")
    if value in {"1", "2", "3"}:
        index = int(value) - 1
        if index >= len(state["recommendations"]):
            raise ValueError("That choice is not present on the current page")
        selected = state["recommendations"][index]["style_id"]
        source = "three-choice"
    elif value in {"auto", "自动选最优"}:
        allowed = [s for s in state["style_scores"] if s["eligible"]]
        if not allowed:
            raise ValueError("No style satisfies the hard constraints")
        selected = allowed[0]["style_id"]
        source = "auto-highest"
    else:
        selected = resolve_style(value)
        source = "user-specified"
        if selected in event.brand.forbidden_styles:
            raise ValueError("Selected style is forbidden by brand rules")
    state["selected_style"] = selected
    state["selection_source"] = source
    write_json(path, state)
    return selected, state
