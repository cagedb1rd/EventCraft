# Design research and rights

访问日期：2026-10-11（Australia/Sydney；实现和验证延续到 2026-10-12）。联网阅读来源文本与出版案例，未下载照片、字体、商业模板或第三方 SVG。下面是原则性启发；项目的布局、插画和图形均为独立代码实现，没有用来源作品充当自己的预览。

| 风格 | 参考来源 | 学习原则 | 许可状态 |
|---|---|---|---|
| swiss-grid | [Cooper Hewitt: A Harmony of Contrasts](https://www.cooperhewitt.org/2018/08/05/aharmonyofcontrasts/) | 内容出发、不对称网格、字体层级与几何对比 | 只引用链接；图片未使用 |
| editorial-minimal | [Pentagram: The Paris Review](https://www.pentagram.com/work/the-paris-review) | 克制刊头、文字与作品留白、阅读尺度 | 客户作品版权；无素材复制 |
| tech-gradient | [Designer AI Conference poster](https://www.behance.net/gallery/232584791/Futuristic-AI-Conference-Poster-Design-2025/modules/1334618877)、[Pentagram Graphcore](https://www.pentagram.com/work/graphcore) | 冷色深度、抽象图形与明确主题焦点 | Behance 标记 All Rights Reserved；仅原则研究 |
| academic-clean | [TUM Call for papers](https://www.mgt.tum.de/fileadmin/mgt.tum.de/campus_heilbronn/global_center_for_family_enterprise/tum-school-of-management-new-venture-team-design-in-the-digital-age-call-for-papers.pdf) | 明确会议信息、理性层级、长文本组织 | 大学资料；不分发原 PDF |
| neo-brutal | [Pentagram Storefront Gala 2026](https://www.pentagram.com/work/storefront-gala-2026) | 硬轮廓、模块节奏、不同物料共享识别 | 专有字形不复刻；原创星形替代 |
| retro-print | [Cooper Hewitt How Posters Work](https://www.cooperhewitt.org/exhibitions/how-posters-work/) | 尺度变化、平面印刷构成、成套图形逻辑 | 博物馆作品版权各异；未复制图片 |
| neon-night | [AI Conference designer study](https://www.behance.net/gallery/232584791/Futuristic-AI-Conference-Poster-Design-2025/modules/1334618877) | 深底荧光对比；项目另行定义夜场门框体系 | 只研究色彩；不复制原构图 |
| warm-playful | [Pentagram Hay Festival](https://www.pentagram.com/work/hay-festival) | 亲和有机线条、多个渠道延续视觉语言 | 原树形识别未使用；项目原创植物图形 |
| luxury-elegant | [Pentagram Rolls-Royce](https://www.pentagram.com/work/rolls-royce-3/story)、[Wedding identity](https://thecordiallyinvited.com/identity) | 克制字体、细节尺度、整套邀请识别 | 专有 Logo 与字体未使用；非品牌合作 |
| sports-dynamic | [Cooper Hewitt design teaching resource](https://www.cooperhewitt.org/wp-content/uploads/2014/05/Making-Design-Teacher-Resource-Packet-.pdf)、[re-inc poster feature](https://www.itsnicethat.com/news/pentagram-re-inc-posters-graphic-design-200320) | 激活对角线、竞技力度、信息清晰 | 只引用来源；自有斜切速度构成 |

同一个研究来源可启发多个抽象原则；不意味着源案例本身属于项目命名的风格。luxury 与 editorial 的结构区分为礼仪中轴/花结和编辑刊头/偏置作品窗；sports 与 neon 分别为速度/对抗和夜场/荧光门框。网络研究没有证明主观设计质量，实际 Gallery 是独立检视对象。

技术依据：[Playwright Page API](https://playwright.dev/python/docs/api/class-page)、[OpenAI Images API](https://developers.openai.com/api/reference/resources/images)、[Responses API](https://developers.openai.com/api/reference/resources/responses)。调用文档不等于已执行外部 API。所有模板字由 Chromium 排版，不由图像模型绘制。
