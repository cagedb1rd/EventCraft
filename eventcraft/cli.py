"""Concrete CLI and equivalent Agent workflow with persistent style selection."""

import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import Error as BrowserError

from .extractors import extract, read_text
from .providers import OpenAIProvider
from .providers.reference import StyleOverride, analyze_references
from .recommendation import profiles, rank, resolve_style
from .recommendation.state import choose, save_recommendations
from .renderer import batch_render, browser, preview_document, render_preview
from .schema import Event, Evidence, issues
from .security import local_file, slugify, write_json


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="eventcraft", description="EventCraft · 10 design systems, 3 recommendations, 1 campaign")
    sub = p.add_subparsers(dest="command", required=True)
    for name in ["extract", "recommend", "render", "all"]:
        c = sub.add_parser(name)
        c.add_argument("input", type=Path)
        c.add_argument("--output", type=Path)
        c.add_argument("--input-root", type=Path, help="Restrict inputs and assets to this directory")
        c.add_argument("--language", choices=["zh", "en", "bilingual"])
        c.add_argument("--ocr", action="store_true")
        c.add_argument("--llm", action="store_true", help="Use official OpenAI Responses extraction")
        c.add_argument("--allow-network", action="store_true")
        c.add_argument("--model", default="gpt-4.1-mini")
        if name in {"recommend", "all", "render"}:
            c.add_argument("--state", type=Path, help="Persistent recommendation directory")
        if name == "recommend":
            c.add_argument("--page", type=int, default=1)
            c.add_argument("--next", action="store_true")
            c.add_argument("--all", action="store_true", dest="all_styles")
            c.add_argument("--weights", type=Path, help="JSON seven-dimension weights totaling 100")
        if name in {"all", "render"}:
            c.add_argument("--style")
            c.add_argument("--style-reference", action="append", default=[], help="Repeat for multiple images")
            c.add_argument("--style-description", default="")
            c.add_argument("--style-override", type=Path, help="Rerender a persisted custom configuration")
            c.add_argument("--vision", action="store_true", help="Analyze reference characteristics through OpenAI")
            c.add_argument("--generate-hero", help="Explicit paid image generation prompt")
            c.add_argument("--auto-style", action="store_true")
            c.add_argument("--select", help="Choose 1/2/3, auto, or any style ID from saved state")
            c.add_argument("--draft", action="store_true")
            c.add_argument("--interactive", action="store_true")
    g = sub.add_parser("gallery")
    g.add_argument("--output", type=Path, default=Path("examples/gallery"))
    g.add_argument("--event", type=Path)
    return p


def get_event(args) -> Event:
    event = extract(args.input, args.input_root, args.ocr)
    if args.llm:
        provider = OpenAIProvider(allow_network=args.allow_network, model=args.model)
        event = provider.extract_event(read_text(local_file(args.input, args.input_root), args.ocr))
    if args.language:
        event.language = args.language
    return event


def recommend(event: Event, directory: Path, page: int = 1, weights=None, all_styles=False, input_root=None) -> dict:
    ranking = rank(event, weights)
    state = save_recommendations(event, directory, page, ranking)
    shown = [dict(s, position=i+1, rank=i+1) for i, s in enumerate(ranking["style_scores"])] if all_styles else state["recommendations"]
    with browser() as active:
        for item in shown:
            if not item["eligible"]:
                continue
            filename = f"previews/{item['style_id']}.png"
            report = render_preview(event, item["style_id"], directory / filename, instance=active, input_root=input_root)
            item["preview_path"] = filename
            item["preview_event_digest"] = report["event_digest"]
            item["preview_checks"] = report["layout"]
    if not all_styles:
        state["recommendations"] = shown
    state["displayed"] = shown
    write_json(directory / "state.json", state)
    write_json(directory / "recommendations.json", state)
    preview_document(event, directory, [s for s in shown if s["eligible"]])
    for item in shown:
        name = profiles()[item['style_id']]['name']
        print(f"{item['position']}. {name} [{item['style_id']}]" + (" [品牌约束冲突]" if not item["eligible"] else ""))
        print("   " + item['reason'])
        print("   取舍：" + item['tradeoff'])
        if item.get("preview_path"):
            print("   预览：" + str(directory / item['preview_path']))
    if len(shown) < 3:
        print("剩余可推荐风格不足三种；可明确指定符合约束的风格或提供自定义参考。")
    return state


def confirm_once(event: Event) -> Event:
    problems = issues(event)
    if not problems:
        return event
    print("请集中确认以下问题：\n" + "\n".join("- " + item for item in problems))
    print('输入一个 JSON 对象补充/修正字段（含 uncertainties: [] 表示这些歧义已经确认）；留空中止：')
    reply = input().strip()
    if not reply:
        raise ValueError("Awaiting required facts")
    patch = json.loads(reply)
    if not isinstance(patch, dict):
        raise ValueError("Confirmation must be a JSON object")
    data = event.model_dump()
    data.update(patch)
    data["confirmed_fields"] = list(dict.fromkeys([*event.confirmed_fields, *patch]))
    for field in patch:
        data["sources"][field] = Evidence(source="user-confirmation", status="confirmed").model_dump()
    confirmed = Event.model_validate(data)
    if issues(confirmed):
        raise ValueError("Confirmation still incomplete:\n" + "\n".join(issues(confirmed)))
    return confirmed


def interactive_style(event: Event, directory: Path) -> tuple[str, dict]:
    state = recommend(event, directory)
    while True:
        print("请选择 1/2/3、自动选最优、换一批、查看全部 10 套、风格 ID，或 reference:图片路径：")
        reply = input().strip()
        if reply in {"换一批", "next"}:
            state = recommend(event, directory, state["page"] + 1)
        elif reply in {"查看全部 10 套", "all"}:
            recommend(event, directory, all_styles=True)
        elif reply.startswith("reference:"):
            return reply, {"selection_source": "reference"}
        else:
            return choose(event, directory, reply)


def gallery(directory: Path, event: Event | None = None) -> None:
    from .renderer.templates import escape
    event = event or Event(
        title="灵感相遇", subtitle="在这里，让新的想法发生", category="community",
        start="2026-11-14T14:00", end="2026-11-14T17:00", timezone="Asia/Shanghai",
        venue="示例艺术空间 · 一层展厅", organizer="EventCraft Demo", registration="无需报名 · 示例活动",
        highlights=["创作分享", "开放交流", "灵感实践"], demo=True,
    )
    cards = []
    with browser() as active:
        for sid, profile in profiles().items():
            batch_render(event, directory / sid, sid, instance=active)
            cards.append(f'<article><h2>{escape(profile["name"])}</h2><p>{sid}</p><div><a href="{sid}/preview.html"><img src="{sid}/poster_portrait.png"></a><img src="{sid}/invitation.png"></div></article>')
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "index.html").write_text('<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>EventCraft Style Gallery</title><style>body{font:16px system-ui;background:#f1efea;margin:40px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:28px}article{background:white;padding:24px}article>div{display:flex;gap:12px;align-items:flex-start}img{width:100%;display:block}a{width:50%}div>img{width:50%}h1{font-size:44px}</style><h1>EventCraft / 10 Design Systems</h1><p>同一虚构活动 · 真实 Chromium 渲染 · 点击海报打开完整物料包</p><main>' + ''.join(cards) + '</main></html>', encoding="utf-8")
    print(f"Gallery generated: {directory / 'index.html'}")


def run(args) -> int:
    if args.command == "gallery":
        gallery(args.output, extract(args.event) if args.event else None)
        return 0
    event = get_event(args)
    if args.command == "extract":
        destination = args.output or Path("output") / slugify(event.title or args.input.stem) / "event.json"
        write_json(destination, event.model_dump())
        write_json(destination.with_name("questions.json"), {"questions": issues(event), "mode": "model" if args.llm else "best-effort"})
        print(f"Extracted: {destination}\n" + "\n".join(issues(event)))
        return 0
    state_dir = args.state or Path("output/.state") / slugify(event.title or args.input.stem)
    if args.command == "recommend":
        directory = args.output or state_dir
        page = args.page
        if args.next:
            if not (directory / "state.json").is_file():
                raise ValueError("No previous page; run recommend first")
            saved = json.loads((directory / "state.json").read_text(encoding="utf-8"))
            from .security import digest
            if saved["event_digest"] != digest(event.model_dump()):
                raise ValueError("Event changed; cannot advance saved recommendations")
            page = saved["page"] + 1
        weights = json.loads(local_file(args.weights, args.input_root).read_text()) if args.weights else None
        recommend(event, directory, page, weights, args.all_styles, args.input_root)
        return 0
    if args.interactive:
        event = confirm_once(event)
    if issues(event) and not args.draft:
        raise ValueError("Facts need confirmation:\n" + "\n".join(issues(event)))
    if args.style:
        event.style = resolve_style(args.style)
    if event.style:
        event.style = resolve_style(event.style)
    refs = args.style_reference or event.assets.style_reference
    ranking = rank(event)
    allowed = [s for s in ranking["style_scores"] if s["eligible"]]
    if not allowed:
        raise ValueError("No style satisfies hard constraints; revise the brand rules")
    selection = {**ranking, "selection_source": "user-specified"}
    style = event.style
    if args.style_override:
        style = style or allowed[0]["style_id"]
        selection["selection_source"] = "reference"
    elif refs:
        style = style or allowed[0]["style_id"]
        selection["selection_source"] = "reference"
    elif style:
        pass
    elif args.select:
        style, selection = choose(event, state_dir, args.select)
    elif args.auto_style:
        style = allowed[0]["style_id"]
        selection["selection_source"] = "auto-highest"
    elif args.interactive:
        style, selection = interactive_style(event, state_dir)
        if style.startswith("reference:"):
            refs = [style.removeprefix("reference:")]
            style = allowed[0]["style_id"]
    else:
        recommend(event, state_dir)
        print("Awaiting style selection; rerun with --select 1/2/3, --auto-style or --style.")
        return 3
    destination = args.output or Path("output") / slugify(event.title or args.input.stem)
    override = None
    if args.style_override:
        override = StyleOverride.model_validate_json(local_file(args.style_override, args.input_root).read_text(encoding="utf-8"))
        if event.style:
            override.base_style = event.style
        style = resolve_style(override.base_style)
    elif refs:
        override = analyze_references(event, refs, style, root=args.input_root,
                                      provider=OpenAIProvider(allow_network=args.allow_network, model=args.model) if args.vision else None,
                                      description=args.style_description or event.style_description)
        style = override.base_style
        for limitation in override.limitations:
            print(limitation)
    if args.generate_hero:
        provider = OpenAIProvider(allow_network=args.allow_network, model=args.model)
        private = Path("output/private-generated") / slugify(event.title or args.input.stem)
        event.assets.hero_image = str(provider.generate_image(args.generate_hero, private / "hero.png").resolve())
    selection["selected_style"] = style
    manifest = batch_render(event, destination, style, draft=args.draft, selection=selection, override=override, input_root=args.input_root)
    print(f"Generated complete campaign: {destination / 'preview.html'}")
    print(f"Style: {manifest['style']} / {style}; batch calls: 1; layout checks: passed")
    return 0


def main(argv=None) -> int:
    try:
        return run(parser().parse_args(argv))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("EventCraft: " + str(exc), file=sys.stderr)
        return 2
    except (EOFError, KeyboardInterrupt):
        print("EventCraft: interaction cancelled; no campaign generated", file=sys.stderr)
        return 130
    except BrowserError:
        print("EventCraft: browser rendering failed; verify Chromium installation and permissions", file=sys.stderr)
        return 2
