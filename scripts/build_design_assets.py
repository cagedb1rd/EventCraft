"""Regenerate the authored machine-readable design catalog and individual guides."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLE_FONTS = {
    "swiss-grid": ("Arial, DengXian, Noto Sans CJK SC, PingFang SC", 700),
    "editorial-minimal": ("Georgia, SimSun, Noto Serif CJK SC, Songti SC", 400),
    "tech-gradient": ("Segoe UI, Microsoft YaHei, Noto Sans CJK SC, PingFang SC", 700),
    "academic-clean": ("DengXian, Noto Sans CJK SC, PingFang SC", 500),
    "neo-brutal": ("Arial Black, SimHei, Noto Sans CJK SC, PingFang SC", 900),
    "retro-print": ("Georgia, SimSun, Noto Serif CJK SC, Songti SC", 700),
    "neon-night": ("Bahnschrift, Microsoft JhengHei, Noto Sans CJK SC, PingFang SC", 700),
    "warm-playful": ("KaiTi, Kaiti SC, Noto Serif CJK SC, Georgia", 600),
    "luxury-elegant": ("Times New Roman, SimSun, Noto Serif CJK SC, Songti SC", 400),
    "sports-dynamic": ("Arial Narrow, Microsoft YaHei, Noto Sans CJK SC, PingFang SC", 900),
}
STYLES = [
    ("swiss-grid", "瑞士网格设计", "Swiss grid", ["#f4f2ec", "#151515", "#db2b21"],
     ["lecture", "exhibition", "forum", "recruitment", "academic"], ["students", "designers", "professionals"],
     ["professional", "casual"], ["设计", "design", "讲座"], "day", "medium", "grid",
     "左侧窄索引栏 / 大字号标题 / 右侧几何圆 / 底部横向信息表", "红色矩形邀请标记，标题与信息左右分栏", "无衬线", "避免装饰性渐变与居中堆叠", "构图鲜明，超长标题需要压缩字号"),
    ("editorial-minimal", "编辑杂志极简风", "Editorial minimal", ["#f6f1e7", "#242621", "#627363"],
     ["exhibition", "community", "lecture", "launch", "wedding"], ["artists", "designers", "professionals"],
     ["professional", "casual"], ["艺术", "art", "文化", "culture"], "day", "low", "editorial",
     "杂志刊头 / 偏置作品窗 / 编辑标题 / 页脚细栏", "开放式纸面，细线将邀请文字与实用信息分开", "衬线", "避免高饱和霓虹与厚边框", "留白丰富，长议程更适合附页"),
    ("tech-gradient", "现代科技渐变风", "Tech gradient", ["#101733", "#f6f8ff", "#8b9cff"],
     ["launch", "lecture", "academic", "workshop", "forum"], ["developers", "students", "professionals"],
     ["professional", "casual"], ["AI", "Agent", "科技", "technology", "digital"], "any", "medium", "space",
     "顶部坐标 / 左对齐标题 / 轨道光环主视觉 / 底部半透明信息区", "短轨道图形与横向卡片，增加阅读空间", "无衬线", "避免假 UI、假数据和在模型图中排关键文字", "科技氛围强，正文应控制密度"),
    ("academic-clean", "学术专业风", "Academic clean", ["#eef3f4", "#183f4b", "#315c69"],
     ["academic", "workshop", "forum", "lecture"], ["researchers", "professionals", "students"],
     ["professional"], ["学术", "academic", "研究", "research", "研讨"], "day", "high", "institutional",
     "顶部细色带 / 左侧书脊 / 编号主题 / 水平知识图形 / 结构化事实表", "邀请正文与日程信息置于分隔线之间", "无衬线", "避免臆造学校徽章和过度宣传", "专业可信，视觉表达相对克制"),
    ("neo-brutal", "年轻大胆风", "Neo brutal", ["#ffe349", "#171717", "#8b3dde"],
     ["recruitment", "market", "community", "opening", "esports"], ["students", "creatives", "young"],
     ["casual"], ["创意", "creative", "校园", "campus"], "day", "medium", "blocks",
     "顶部分裂标签 / 硬阴影标题块 / 错位圆形贴纸 / 黑色信息模块", "邀请标题做成票券，信息区保持硬边框", "无衬线", "避免无序旋转正文或牺牲可读性", "年轻醒目，不适合庄重礼仪"),
    ("retro-print", "复古印刷风", "Retro print", ["#efe0bd", "#3b3024", "#9a3e29"],
     ["market", "night-party", "community", "opening", "birthday"], ["creatives", "artists", "young"],
     ["casual"], ["复古", "retro", "音乐", "music", "市集"], "any", "medium", "print",
     "双线印刷边框 / 拱形日晕 / 衬线标题 / 半色调纸张 / 票券式底栏", "横向印刷徽记与邀请称谓，减少主视觉高度", "衬线", "纹理不能覆盖文字、不能虚构历史奖项", "温厚怀旧，色彩表现较柔和"),
    ("neon-night", "霓虹夜生活风", "Neon night", ["#130e25", "#faf4ff", "#ef75f3"],
     ["night-party", "esports", "community"], ["young", "gamers", "music fans"],
     ["casual"], ["夜间", "night", "DJ", "音乐", "party", "霓虹"], "night", "low", "neon",
     "左上夜场标签 / 发光门框 / 下部居中强标题 / 时间地点发光线", "门框缩为横向霓虹边线，称谓与细节上下分组", "无衬线", "日间体育不应默认使用；不让正文字体发虚", "夜间吸睛，不适合密集学术信息"),
    ("warm-playful", "温暖手绘风", "Warm playful", ["#fff3db", "#4e392b", "#a84b36"],
     ["birthday", "workshop", "community", "market", "wedding"], ["families", "children", "friends"],
     ["casual"], ["生日", "birthday", "手作", "craft", "亲子", "温暖"], "day", "medium", "organic",
     "顶部手绘枝叶 / 便笺式标题 / 花朵太阳插画 / 圆角邀请信纸", "短花边与亲切称谓，正文纸卡占比增加", "无衬线", "避免伪手写中文字与幼稚化正式会议", "亲和温暖，正式商务气质较弱"),
    ("luxury-elegant", "奢华典雅风", "Luxury elegant", ["#f5f0e5", "#18392d", "#876d3c"],
     ["wedding", "dinner", "awards", "forum"], ["guests", "executives", "couples", "professionals"],
     ["ceremonial", "professional"], ["婚礼", "wedding", "晚宴", "gala", "颁奖", "VIP"], "night", "low", "ceremony",
     "双层细线框 / 精致几何花结 / 衬线主标题 / 中轴留白 / 礼仪信息组", "把礼仪称谓置于主标题上，细信息与报名做信笺底栏", "衬线", "避免金色渐变堆砌、虚假家徽和假主办方 Logo", "礼仪感突出，长文本会降低高级留白感"),
    ("sports-dynamic", "运动竞技风", "Sports dynamic", ["#0e2331", "#f8faf7", "#d6f349"],
     ["sports", "esports", "recruitment"], ["athletes", "students", "gamers", "young"],
     ["casual", "professional"], ["足球", "篮球", "跑步", "比赛", "sport", "race", "竞技"], "day", "medium", "diagonal",
     "右侧巨大日期数字 / 斜切速度带 / 左侧竞技标题 / 对抗队伍栏 / 硬信息底块", "队伍和时间靠前，速度图形移到侧边，正文不倾斜", "无衬线", "竞技与夜生活分开；不虚构队伍、赛程或编号", "速度感强，仪式性活动适配较弱"),
]


def main():
    target = ROOT / "eventcraft/data"
    target.mkdir(parents=True, exist_ok=True)
    public = ROOT / "assets/styles"
    public.mkdir(parents=True, exist_ok=True)
    guides = ROOT / "references/style-guides"
    guides.mkdir(parents=True, exist_ok=True)
    profiles = {}
    for row in STYLES:
        sid, name, en, colors, types, audience, formality, keys, time, density, family, poster, invitation, font, negative, tradeoff = row
        profile = {
            "id": sid, "name": name, "name_en": en, "palette": colors, "types": types,
            "audience": audience, "formality": formality, "keywords": keys, "time": time,
            "density": density, "family": family, "hero": "optional", "language": ["zh", "en", "bilingual"],
            "avoid": ["ceremonial"] if sid in {"neo-brutal", "neon-night", "sports-dynamic"} else [],
            "brand": {"recolorable": True, "preserve_logo": True, "contrast_min": 4.5},
            "tokens": {"grid_columns": 12 if sid == "swiss-grid" else 6, "margin": 72,
                       "title_px": 162 if sid == "sports-dynamic" else 148 if font == "无衬线" else 140,
                       "body_px": 35, "small_px": 24, "invitation_title_px": 112, "square_title_px": 96,
                       "heading_fonts": TITLE_FONTS[sid][0], "heading_weight": TITLE_FONTS[sid][1],
                       "font": "serif" if font == "衬线" else "sans", "cjk_sans": "Microsoft YaHei, Noto Sans CJK SC, PingFang SC",
                       "cjk_serif": "SimSun, Noto Serif CJK SC, Songti SC", "whitespace": "generous" if density == "low" else "balanced",
                       "alignment": "center" if sid in {"luxury-elegant", "neon-night", "retro-print"} else "left"},
            "layout": {"poster": poster, "invitation": invitation}, "negative": negative, "tradeoff": tradeoff,
        }
        profiles[sid] = profile
        (public / f"{sid}.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        guide = f"""# {name} / {en}

定位：{family}。适用：{', '.join(types)}。这是一套原创布局，网络参考仅用于原则研究。

## Tokens 与字体

背景 `{colors[0]}`，正文 `{colors[1]}`，强调 `{colors[2]}`。采用系统{font}字体；中文分别回退 Microsoft YaHei / Noto Sans CJK SC 或 SimSun / Noto Serif CJK SC。系统字体不进入仓库。
标题字体栈：`{TITLE_FONTS[sid][0]}`；字重 {TITLE_FONTS[sid][1]}。中英文各自回退到可用字体，manifest 记录实际使用结果。温暖风使用系统楷体，保留亲切的书写感。
海报标题上限 {profile['tokens']['title_px']} px，正文 35 px，信息 40 px，标签 24 px；邀请函标题 112 px，方图标题 96 px。1080 宽画布安全边距 72 px（各风格另有轴线与框线边距）。实际字体尺寸由 Chromium 度量，优先压缩装饰空间，再根据可用区域收缩，达到下限仍溢出则失败。

## 构图与成套适配

海报：{poster}。
邀请函：{invitation}。使用相同颜色、图案和字体，在 1080×1350 上重排正文，不裁切竖版。
方图压缩图形区并减少标题上限；A4 重新采用邀请式版式并在 PDF 中保留矢量文字。

## 适配与负面约束

长标题按真实字宽自动换行，不截断日期地点报名；中英混排使用 `overflow-wrap:anywhere`，英文保持自然词界。可省略可选的视觉副文，但原始信息保留在 event.json 和完整文案中。没有主图仍使用自有 SVG/几何装饰；用户主图、Logo 使用 contain，二维码有白色静区。
按浏览器度量的标题宽度判断短/中/长标题，平衡换行；长标题在瑞士与运动海报中由左右分栏展开为全宽标题，其他风格压缩装饰区。结构先适配，字号再收缩。
{negative}。正文颜色自动调整至对背景至少 4.5:1；品牌禁止色先过滤。图案不可冒充真实徽章或活动事实。

取舍：{tradeoff}。
"""
        (guides / f"{sid}.md").write_text(guide, encoding="utf-8")
    catalog = {"ranking_version": "1.0.0", "weights": {"type": 30, "audience": 20, "formality": 15, "scene": 10, "density": 10, "brand": 10, "readability": 5}, "styles": profiles}
    text = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    (target / "style-profiles.json").write_text(text, encoding="utf-8")
    (public / "style-profiles.json").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
