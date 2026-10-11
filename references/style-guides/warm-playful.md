# 温暖手绘风 / warm-playful

十套预设是艺术指导、字体与构图契约；每个新活动重新构思主体，不依赖本地 image/。

## 艺术指导

Original warm gouache and cut-paper scene expressing the current event. Small anonymous people and handmade objects only when relevant, ochre/coral/sage pigments, charming natural detail on cream paper.

实际标题长度、文字量和输出比例由 composition.py 在生成前计算自然留白；同一规范坐标指导宿主图像工具与渲染器。没有固定主体或统一标题板。

## 字体契约

- 中文标题：KaiTi → Kaiti SC → Noto Serif SC → SimSun → Songti SC → Noto Serif CJK SC。
- 英文标题：Gabriola → Georgia。
- 副标题：Noto Serif SC → SimSun → Songti SC → Noto Serif CJK SC。
- 信息文字：Noto Sans SC → Microsoft YaHei → PingFang SC → Noto Sans CJK SC。
- 日期数字：Arial → Noto Sans SC。
- 字重 600，字形 normal，字距 0.03 em，行高 1.3，left 对齐。
- 角色比例：{'title': 1, 'subtitle': 0.23, 'information': 0.25, 'labels': 0.13}。
- 分行：balance measured glyph widths; keep short CJK phrases and Latin words; strict Chinese punctuation。
- 混排：Latin display family followed by native CJK family; no forced uppercasing of Chinese。
- 长标题：reserve more natural negative space before generation; expand the title region and measure real fonts before export。

使用用户已安装或有授权的字体，不打包商业字体。实际字体回退写入 manifest；字号按浏览器真实测量适配。

## 文字与图像融合

使用自然低纹理留白；禁止把不透明标题矩形、日期条、页脚底板作为默认补救。Swiss/Brutalist/Retro 几何形可以是原创艺术语言，不能临时遮住复杂主视觉。实际背景采样后仍不可读时，必须重新构图或生成并查看成品。

海报仅保留名称、短副标题、自然日期、地点和必要 CTA/品牌。默认隐藏内部时区；QR 只在明确扫码意图或 qr_policy=show 时产生。无码不留框；长介绍、费用和流程留在邀请函与文案。

## 成套导出

遵循 [宿主图像流程](../image-generation.md)，实际调用内置 ImageGen，导入真实素材并绑定活动、风格和哈希。方图/A4 留白不足时生成 --ratio square/print 比例素材；没有变体时完整适配原图。邀请函按活动选择登机牌、票券、正式卡或折页，使用独立版式。折页输出内外展开与两页 PDF。
