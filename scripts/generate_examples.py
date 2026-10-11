"""Generate five complete fictional campaigns and the actual selection comparison."""

from pathlib import Path

from eventcraft.cli import recommend
from eventcraft.extractors import extract
from eventcraft.recommendation import rank, shortlist
from eventcraft.recommendation.state import choose
from eventcraft.renderer import batch_render, browser
from eventcraft.security import write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    lecture = extract(ROOT / "examples/inputs/lecture.json")
    state_dir = ROOT / "examples/recommendation"
    recommend(lecture, state_dir)
    chosen, state = choose(lecture, state_dir, "1")
    write_json(state_dir / "choice.json", {"user_reply": "1", "style_id": chosen, "source": state["selection_source"]})
    with browser() as active:
        for name in ["lecture", "launch", "birthday", "dinner", "sports"]:
            event = extract(ROOT / f"examples/inputs/{name}.json")
            ranking = rank(event)
            style = shortlist(ranking)[0]["style_id"]
            selection = state if name == "lecture" else {**ranking, "selection_source": "auto-highest", "selected_style": style}
            batch_render(event, ROOT / "examples/generated" / name, chosen if name == "lecture" else style,
                         selection=selection, instance=active)
            print(f"Generated {name}: {style}", flush=True)


if __name__ == "__main__":
    main()
