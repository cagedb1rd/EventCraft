# EventCraft 1.0.0 本地验收记录

验收日期：2026-10-12。运行环境：Windows、Python 3.12.14、Playwright 与本机 Chrome 154.0.8037.98。Chromium 下载版未安装，本机 Chrome 回退实际用于全部渲染。检查的是项目生成的文件，没有用示意图替代成品。

## 自动化结果与可重现命令

| 检查 | 实际结果 |
|---|---|
| `pytest -q --junitxml=docs/test-results.xml` | 86 项通过，包含真实浏览器集成测试 |
| `ruff check eventcraft scripts tests` | 通过 |
| `python scripts/validate_skill.py` | Skill frontmatter、资源链接与 metadata 通过 |
| skill-creator `quick_validate.py .` | Skill is valid |
| `python scripts/generate_examples.py` | 五套完整虚构活动物料生成成功 |
| `python scripts/generate_style_gallery.py` | 十套独立海报和邀请函生成成功 |
| `python scripts/build_showcase.py` | 真实三选一与 Gallery 截图生成成功 |
| `python scripts/build_title_showcase.py` | 短、中、长标题三套实际渲染与边界检查通过 |
| `python scripts/record_cli_demo.py` | recommend 与 select 2 的真实命令成功，UTF-8 记录已保存 |
| `python scripts/verify_outputs.py` | 15 个完整公开物料包重新打开、尺寸/哈希/事实检查通过 |
| `python -m build --no-isolation` | wheel 与源码分发包构建成功 |
| `python scripts/package_skill.py` | 可迁移完整 Skill ZIP 构建成功 |
| `python scripts/isolated_smoke.py` | 从独立目录使用已安装 wheel 和迁移后的 Skill 各生成一套完整物料 |
| `python scripts/release_check.py` | 跟踪范围、明显凭据模式与本地文档链接检查通过 |

Windows 环境命令通过 `.venv\Scripts\python.exe` 运行。测试原始报告：[test-results.xml](test-results.xml)；文件级核验：[artifact-audit.json](artifact-audit.json)；真实命令记录：[recommendation-terminal.txt](recommendation-terminal.txt)。输出包的 `manifest.json` 逐项保留尺寸、字形字体、文字矩形与哈希。

## 验证覆盖

86 项测试覆盖必填缺失/冲突、来源证据、JSON/文本/MD/DOCX/文本 PDF 抽取、时区与夏令时、七维推荐评分、品牌硬约束、三选一与换批不重复、显式/自动选择、状态失效、交互补充、事实一致、路径边界、图片限制、HTML 转义、损坏参考图、多图与隐私、原始素材保留、自定义参考覆盖重放、网络启用与 Provider 请求契约。

十套风格分别使用正常、中英超长、短标题跨日内容，在竖版/邀请函/方图中渲染，共 90 个布局组合。检查真实文字范围、横向溢出、画布越界、主要模块重叠与图片加载；短标题还检查放大后的字号下限，长标题检查瑞士/运动风自动展开结构。五个完整活动集成测试检查成品 PNG 尺寸、A4 PDF 页面、离线 HTML、四类文案事实和批量入口。二维码从原文件与完整成品海报实际解码，验证内容与提供的 URL 相同。

公开样例包含讲座、科技发布、生日、典雅晚宴、体育比赛五套完整物料；另有同一固定活动的十风格完整 Gallery。共 **45 张成品 PNG、30 个 PDF、60 个已核验布局**，另有 3 张真实推荐预览、3 张标题长度对照以及文档总览截图。公开活动均为 Demo，示例 URL 不是可报名活动，manifest 不标记为可发布。

## 视觉检查与修复

已查看 [十风格实际总览](images/style-contact-sheet.png)、[三选一到成套输出](images/selection-workflow.png)、[标题长度对照](images/title-adaptation.png)，并用 Poppler 将最新 A4 海报和正式邀请函 PDF 栅格化检查。字体由系统提供，实际使用 DengXian、Microsoft YaHei、SimSun、SimHei、KaiTi、Microsoft JhengHei 及相应英文字体；不在仓库内复制系统字体。

开发期间修复了中文行高不足造成的裁切、强调色与正文对比度混用、A4 海报误用邀请称谓、旧二维码/参考覆盖文件残留、运动方图装饰越界引发的过度缩字，以及二维码缩放模糊。根据实际反馈，标题与关键事实整体放大，十套标题使用不同字体栈/字重；长标题按实际字宽先展开布局和压缩装饰，再缩小字体。`title_layout`、`title_lines` 和 `font_sizes` 写入每个布局检查记录。

## 尚未验证与实际边界

- 官方 OpenAI 理解、视觉与图像生成适配器已做离线请求/错误契约测试，**未使用真实凭据执行付费 API**；账户模型权限、实时服务响应和生成质量未验证。
- 本机没有 Tesseract 和相应 OCR 语言包，截图 OCR 没有真实执行。扫描 PDF 需要 Agent 视觉理解或外部转录；纯文本抽取不宣称语义理解。
- 实际端到端运行仅覆盖 Windows/Python 3.12/Chrome。Linux/macOS、其他 Python 版本、各 Agent 客户端安装与远端 GitHub Actions 仍需对应环境验证。CI 已配置 CJK 字体与完整测试，尚未远程触发。
- 无视觉模型的参考分析只提取颜色，不理解字体、网格或构图。文字风格偏好映射到已实现的原创设计系统；不会复制参考图。跨平台字体回退会改变具体字形。
- 多语输出保留用户提供的活动名称/地址，不自动翻译事实。URL 只做语法验证，未联网检查可用性。原始二维码保留内容，未声称验证其业务有效性。
- A4 PDF 为 RGB、有矢量文字的浏览器打印文件，未提供 CMYK、出血与印刷厂色彩校准。极端密集内容若达到最小字号仍放不下，会明确失败。
- 已准备 MIT、双语 README、贡献指南、CI、依赖锁定、迁移包和本地 Git 提交；**没有创建 GitHub 仓库、配置远程或上传文件**。公开发布由维护者执行。
