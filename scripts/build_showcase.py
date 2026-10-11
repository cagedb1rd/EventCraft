"""Capture offline HTML showcases built from genuine renderer outputs."""

from pathlib import Path

from PIL import Image, ImageDraw

from eventcraft.recommendation import profiles
from eventcraft.renderer import browser

ROOT = Path(__file__).resolve().parents[1]


def main():
    directory = ROOT / "docs/images"
    directory.mkdir(parents=True, exist_ok=True)
    # Original tiny palette asset for a reproducible reference command, not borrowed artwork.
    palette = Image.new("RGB", (800, 400), "#18392d")
    draw = ImageDraw.Draw(palette)
    draw.rectangle((400, 0, 600, 400), fill="#f5f0e5")
    draw.rectangle((600, 0, 800, 400), fill="#876d3c")
    palette.save(ROOT / "examples/inputs/palette.png")
    cards = ''.join(f'<article><h2>{p["name"]}</h2><p>{sid}</p><div><img src="../../examples/gallery/{sid}/poster_portrait.png"><img src="../../examples/gallery/{sid}/invitation.png"></div></article>' for sid, p in profiles().items())
    gallery = '<!doctype html><html lang="zh"><meta charset="utf-8"><style>body{margin:35px;background:#eeeae2;color:#202321;font-family:"Microsoft YaHei",system-ui}h1{font-size:44px;margin:0}header{margin-bottom:28px}main{display:grid;grid-template-columns:repeat(5,1fr);gap:18px}article{background:#faf9f6;padding:15px}h2{font-size:21px;margin:0 0 8px}p{font-size:12px;margin:6px 0 15px;color:#65645e}article>div{display:flex;align-items:flex-start;gap:8px}img{width:calc(50% - 4px)}</style><header><h1>EventCraft / 10 Design Systems</h1><p>同一虚构活动 · 十套原创设计系统 · 真实海报与配套邀请函</p></header><main>' + cards + '</main></html>'
    (directory / "style-contact-sheet.html").write_text(gallery, encoding="utf-8")
    rec = ''.join(f'<figure><img src="../../examples/recommendation/previews/{sid}.png"><figcaption>{i+1}. {profiles()[sid]["name"]}</figcaption></figure>' for i, sid in enumerate(["tech-gradient", "swiss-grid", "academic-clean"]))
    outputs = ''.join(f'<figure><img src="../../examples/generated/lecture/{name}.png"><figcaption>{label}</figcaption></figure>' for name, label in [("poster_portrait", "1080×1920 主海报"), ("poster_square", "1080×1080 社媒图"), ("invitation", "1080×1350 邀请函")])
    workflow = '''<!doctype html><html lang="zh"><meta charset="utf-8"><style>body{margin:38px;background:#f1eee6;color:#182125;font-family:"Microsoft YaHei",system-ui}h1{font-size:45px;letter-spacing:-1px;margin:0}header p{font-size:17px;color:#657077}.top{display:grid;grid-template-columns:1fr 2fr;gap:25px;margin:30px 0}.input{padding:28px;background:#18392d;color:#fff;border-radius:14px}.input h2{font-size:21px}.input p{font-size:19px;line-height:1.75;margin:8px 0}.options,.outputs{display:flex;gap:22px;align-items:flex-start}figure{margin:0;flex:1}figure img{display:block;width:100%;background:#dedacf;object-fit:contain}figcaption{font-size:15px;margin-top:12px}.options img{height:255px}.outputs img{height:485px}.selected{background:white;padding:25px;border:1px solid #ddd9cd}.selected h2{font-size:25px;margin:0 0 22px}.note{margin-top:22px;font-size:15px;color:#69706c}</style><header><h1>EventCraft / 从活动信息到整套物料</h1><p>真实渲染与选择状态 · 示例活动为虚构 Demo · 无 API Key</p></header><section class="top"><div class="input"><h2>01 / 输入事实</h2><p>AI Agent 实战分享会</p><p>2026.10.26 14:00–16:30</p><p>Asia/Shanghai</p><p>示例大学 · 创新楼报告厅</p><p>学生与开发者 · 免费</p></div><div><h2>02 / 三选一实际预览</h2><div class="options">''' + rec + '</div></div></section><section class="selected"><h2>03 / 用户选择 1 → 一次生成完整物料包</h2><div class="outputs">' + outputs + '</div><p class="note">另含 A4 海报 PDF、正式邀请函 PDF、4 类文案、event.json、manifest.json 和离线预览页。每个成品读取同一份活动事实。</p></section></html>'
    (directory / "selection-workflow.html").write_text(workflow, encoding="utf-8")
    with browser() as active:
        page = active.new_page(viewport={"width": 1600, "height": 1100}, device_scale_factor=1)
        for name in ["style-contact-sheet", "selection-workflow"]:
            page.goto((directory / (name + ".html")).as_uri(), wait_until="load")
            page.evaluate("document.fonts.ready")
            assert page.locator("img").evaluate_all("xs=>xs.every(i=>i.complete&&i.naturalWidth)")
            page.screenshot(path=str(directory / (name + ".png")), full_page=True)
        page.goto((ROOT / "examples/recommendation/recommendations.html").as_uri())
        page.screenshot(path=str(directory / "recommendation-browser.png"), full_page=True)
        page.close()
    gallery_md = "# Style Gallery\n\n全部由同一固定虚构活动和本项目 Chromium 渲染器产生。点击海报或邀请函可查看原尺寸图。离线页面：[Gallery](../examples/gallery/index.html)。重现：`python scripts/generate_style_gallery.py`。\n\n"
    gallery_md += "![十风格总览](images/style-contact-sheet.png)\n\n"
    for sid, p in profiles().items():
        gallery_md += f"## {p['name']} / `{sid}`\n\n{p['layout']['poster']}。邀请函：{p['layout']['invitation']}。\n\n| 主海报 | 邀请函 |\n|---|---|\n| ![海报](../examples/gallery/{sid}/poster_portrait.png) | ![邀请函](../examples/gallery/{sid}/invitation.png) |\n\n[完整物料与检查](../examples/gallery/{sid}/preview.html) · [设计规范](../references/style-guides/{sid}.md)\n\n"
    (ROOT / "docs/style-gallery.md").write_text(gallery_md.rstrip() + "\n", encoding="utf-8")
    print("Showcase screenshots and gallery document generated")


if __name__ == "__main__":
    main()
