"""Render real short/medium/long title examples through the adaptive layout pipeline."""

from pathlib import Path

from eventcraft.extractors import extract
from eventcraft.renderer import asset_images, browser, palette_for, prepare
from eventcraft.renderer.templates import escape, sheet_html
from eventcraft.security import write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    destination = ROOT / "docs/images"
    event = extract(ROOT / "examples/inputs/lecture.json")
    titles = [
        ("short", "灵感相遇"),
        ("medium", "AI Agent 实战分享会"),
        ("long", "人工智能时代的创作实践：从灵感探索到跨学科协作"),
    ]
    results, cards = [], []
    with browser() as active:
        page = active.new_page(viewport={"width": 1080, "height": 1920})
        for name, title in titles:
            sample = event.model_copy(deep=True)
            sample.title = title
            source = sheet_html(sample, "swiss-grid", 1080, 1920, "portrait", palette_for(sample, "swiss-grid"), asset_images(sample, style="swiss-grid"))
            rendered, report = prepare(page, source, 1080, 1920)
            (destination / f"title-{name}.html").write_text(rendered, encoding="utf-8")
            page.screenshot(path=str(destination / f"title-{name}.png"))
            results.append({"title": title, "layout": report["title_layout"], "lines": report["title_lines"],
                            "size": report["font_sizes"][0]["size"], "passed": report["passed"],
                            "fonts": report["actual_fonts"]})
            cards.append(f'<figure><img src="title-{name}.png"><figcaption>{escape(title)}<br>{escape(report["title_layout"])} · {report["title_lines"]} 行 · {report["font_sizes"][0]["size"]}</figcaption></figure>')
        html = '<!doctype html><html lang="zh"><meta charset="utf-8"><style>body{background:#f1eee6;color:#182125;margin:35px;font-family:"Microsoft YaHei",sans-serif}h1{font-size:40px}main{display:flex;gap:25px}figure{flex:1;min-width:0;margin:0}img{width:100%;display:block}figcaption{overflow-wrap:anywhere;font-size:20px;line-height:1.6;margin-top:15px}</style><h1>标题长度自适应 / 真实渲染</h1><p>同一虚构活动 · 同一瑞士设计系统 · 字宽度量、平衡换行、长标题展开全宽</p><main>' + ''.join(cards) + '</main></html>'
        (destination / "title-adaptation.html").write_text(html, encoding="utf-8")
        page.set_viewport_size({"width": 1500, "height": 1100})
        page.goto((destination / "title-adaptation.html").as_uri())
        page.screenshot(path=str(destination / "title-adaptation.png"), full_page=True)
        page.close()
    write_json(ROOT / "docs/title-adaptation.json", results)
    print("Rendered and checked three actual title lengths")


if __name__ == "__main__":
    main()
