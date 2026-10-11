"""Synchronize public profiles/guides from the current canonical design data."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    data = ROOT / "eventcraft/data"
    catalog = json.loads((data / "style-profiles.json").read_text(encoding="utf-8"))
    visual = json.loads((data / "visual-systems.json").read_text(encoding="utf-8"))
    fonts = json.loads((data / "typography.json").read_text(encoding="utf-8"))
    # visual-systems uses a styles object; accept its canonical container.
    visual = visual.get("styles", visual)
    public = ROOT / "assets/styles"
    guides = ROOT / "references/style-guides"
    public.mkdir(parents=True, exist_ok=True)
    guides.mkdir(parents=True, exist_ok=True)
    for sid, profile in catalog["styles"].items():
        t, v = fonts[sid], visual[sid]
        profile["typography"] = t
        profile["palette"] = v["palette"]
        profile["tokens"].update(heading_fonts=", ".join(t["en_title"] + t["zh_title"]),
                                 heading_weight=t["weight"], alignment=t["alignment"])
        (public / f"{sid}.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        roles = "\n".join(f"- {label}：{' → '.join(t[key])}。" for key, label in
                          [("zh_title", "中文标题"), ("en_title", "英文标题"), ("subtitle", "副标题"),
                           ("information", "信息文字"), ("numbers", "日期数字")])
        guide = f"""# {profile['name']} / {sid}

十套预设是艺术指导、字体与构图契约；每个新活动重新构思主体，不依赖本地 image/。

## 艺术指导

{v['art']}

实际标题长度、文字量和输出比例由 composition.py 在生成前计算自然留白；同一规范坐标指导宿主图像工具与渲染器。没有固定主体或统一标题板。

## 字体契约

{roles}
- 字重 {t['weight']}，字形 {t['shape']}，字距 {t['tracking']} em，行高 {t['leading']}，{t['alignment']} 对齐。
- 角色比例：{t['scale']}。
- 分行：{t['line_break']}。
- 混排：{t['bilingual']}。
- 长标题：{t['long_title']}。

使用用户已安装或有授权的字体，不打包商业字体。实际字体回退写入 manifest；字号按浏览器真实测量适配。

## 文字与图像融合

使用自然低纹理留白；禁止把不透明标题矩形、日期条、页脚底板作为默认补救。Swiss/Brutalist/Retro 几何形可以是原创艺术语言，不能临时遮住复杂主视觉。实际背景采样后仍不可读时，必须重新构图或生成并查看成品。

海报仅保留名称、短副标题、自然日期、地点和必要 CTA/品牌。默认隐藏内部时区；QR 只在明确扫码意图或 qr_policy=show 时产生。无码不留框；长介绍、费用和流程留在邀请函与文案。

## 成套导出

遵循 [宿主图像流程](../image-generation.md)，实际调用内置 ImageGen，导入真实素材并绑定活动、风格和哈希。方图/A4 留白不足时生成 --ratio square/print 比例素材；没有变体时完整适配原图。邀请函按活动选择登机牌、票券、正式卡或折页，使用独立版式。折页输出内外展开与两页 PDF。
"""
        (guides / f"{sid}.md").write_text(guide, encoding="utf-8")
    text = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    (data / "style-profiles.json").write_text(text, encoding="utf-8")
    (public / "style-profiles.json").write_text(text, encoding="utf-8")
    print("Canonical profiles, public mirrors and ten typography guides synchronized")


if __name__ == "__main__":
    main()
