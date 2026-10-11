# EventCraft

**输入活动资料 → 十选三真实预览 → 选择一种 → 一次生成整套宣传物料。**

![真实三选一及最终物料](docs/images/selection-workflow.png)

以上来自项目自己的 Chromium 渲染器，活动为虚构 Demo。 [English](README.en.md) · [完整 Style Gallery](docs/style-gallery.md) · [验收结果](docs/verification.md)

EventCraft 同时是可安装的 Agent Skill 和独立 Python CLI：不用 API Key 就能输出 1080×1920 主海报、1080×1080 方图、1080×1350 邀请函、A4 海报 PDF、正式邀请函 PDF、四类中英文文案、规范化事实、manifest 和离线预览页。十套设计有各自的结构、字体、装饰和信息排布，支持 Logo、主图、讲者照片、原始二维码及参考图偏好。

## 三分钟开始

需要 Python 3.11+、Chromium、中文字体。Windows 使用已有 Microsoft YaHei / SimSun；macOS 使用 PingFang / Songti；Linux 安装 `fonts-noto-cjk`。不随仓库分发系统字体。

```sh
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m playwright install chromium
eventcraft all examples/inputs/lecture.json --auto-style --output output/lecture
```

打开 `output/lecture/preview.html` 即可。模板生成过程完全离线；安装依赖/浏览器本身需要网络。Windows 已有 Chrome/Edge 可自动回退，也可用 `EVENTCRAFT_BROWSER` 指定浏览器路径。首次安装按系统策略可能需要激活 PowerShell 脚本，或直接运行 `.venv\Scripts\eventcraft.exe`。

## 默认三选一：可执行、可恢复

```sh
eventcraft recommend examples/inputs/lecture.json --output output/selection
# 打开 output/selection/recommendations.html，看真实预览
eventcraft all examples/inputs/lecture.json --select 2 --state output/selection --output output/chosen
```

真实执行记录见 [recommendation-terminal.txt](docs/recommendation-terminal.txt)。本例首批为科技渐变、瑞士网格、学术专业，每项给出依据和取舍，选择后只调用一次批量入口。

```sh
eventcraft recommend examples/inputs/lecture.json --output output/selection --next
eventcraft recommend examples/inputs/lecture.json --page 2 --output output/page2
# 仅主动请求时看全部十套
eventcraft recommend examples/inputs/lecture.json --all --output output/all-styles
# 任意风格可以直接指定
eventcraft render examples/inputs/lecture.json --style retro-print --output output/retro
```

状态写入 `state.json`、评分和输入/config 摘要写入 `recommendations.json`；原资料变化后数字选择失效。自动模式从满足硬约束的全体风格选最高分，换批按稳定次序不重复。评分是工程规则，不是审美科学。自定义权重使用 `--weights weights.json`。详见 [推荐算法](docs/style-recommendation.md)。

## 资料输入与事实确认

```sh
eventcraft extract examples/inputs/lecture.md --output output/extracted/event.json
eventcraft all examples/inputs/lecture.md --interactive --output output/interactive
```

支持文本、Markdown、TXT、DOCX、带文本层 PDF，以及可选 Tesseract OCR 的截图。CLI 无模型时采用字段标签和保守正则，不宣称理解隐含语义。`extract` 生成 `questions.json`，缺年份/时间/时区/地点/报名方式或存在冲突时，最终生成返回明确错误。交互一次集中接受 JSON 补充；Agent 模式以自然语言集中提问。允许 `--draft`，会带草稿标记，manifest 不标为可发布。示例无任何真实个人信息，`example.org` 地址仅测试二维码。

中文默认；`--language en` 使用英文标签和英文文案，保留原活动事实，不擅自翻译名称地址。`bilingual` 支持用户自带中英混排内容。 [数据契约](references/event-schema.md)

## 十套独立视觉系统

![十风格真实渲染概览](docs/images/style-contact-sheet.png)

| ID | 中文名称 | 结构与用途 |
|---|---|---|
| swiss-grid | 瑞士网格设计 | 索引轴线、不对称网格、讲座/论坛 |
| editorial-minimal | 编辑杂志极简风 | 刊头、编辑留白、艺术/文化 |
| tech-gradient | 现代科技渐变风 | 空间轨道、信息卡片、AI/发布 |
| academic-clean | 学术专业风 | 机构书脊、细分隔线、学术/培训 |
| neo-brutal | 年轻大胆风 | 硬边模块、撞色贴纸、招新/市集 |
| retro-print | 复古印刷风 | 拱形日晕、纸纹票券、复古/音乐 |
| neon-night | 霓虹夜生活风 | 发光门框、夜间音乐/电竞派对 |
| warm-playful | 温暖手绘风 | 原创植物线稿、便笺纸卡、生日/亲子 |
| luxury-elegant | 奢华典雅风 | 礼仪中轴、细线花结、婚礼/晚宴 |
| sports-dynamic | 运动竞技风 | 斜切速度线、真实日期数字、体育/竞技 |

[十套海报 + 邀请函](docs/style-gallery.md)。重新生成：`eventcraft gallery --output output/gallery`；开源 Gallery 固定样例：`python scripts/generate_style_gallery.py`。五套完整物料：`python scripts/generate_examples.py`。

标题字体按风格使用不同字体栈与字重，并根据真实字宽平衡换行。短标题保持醒目；长标题先展开阅读区、压缩装饰，再收缩字号。[短/中/长标题真实对照](docs/images/title-adaptation.png)，重现：`python scripts/build_title_showcase.py`。每个 manifest 记录实际字体、标题行数与布局选择。

## 参考图、自有素材与可选 Provider

```sh
# 可运行的原创参考色板样例；其图片仅提供色彩，版式显式指定
eventcraft render examples/inputs/dinner.json --style luxury-elegant --style-reference examples/inputs/palette.png --style-description '奢华典雅风，细线与留白' --output output/custom
```

`--style-reference` 可重复最多五次；参考图与 `assets.hero_image` 分开。无视觉模型只分析颜色，明确报告无法理解网格、字体和构图；使用 `--style` 或命名风格的描述指定原创基础布局。输出 `style_override.json` 记录 palette、基础布局、描述和 hashes，可直接重渲染，私人原图不写入成品。品牌颜色优先，正文对比度至少 4.5:1。用户照片/Logo 用 contain，原始二维码不改内容；真实 URL 可生成二维码，缺 URL 不造二维码。

可选官方 OpenAI Provider，需要 `OPENAI_API_KEY` 环境变量、账户可用模型权限，并可能产生 API 费用。所有请求均需 `--allow-network`：

```sh
eventcraft extract examples/inputs/lecture.md --llm --allow-network --output output/model-event.json
eventcraft render examples/inputs/dinner.json --style-reference examples/inputs/palette.png --vision --allow-network --output output/vision
eventcraft render examples/inputs/launch.json --auto-style --generate-hero 'Original abstract orbital sculpture, no text' --allow-network --output output/with-art
```

默认理解模型 `gpt-4.1-mini` 可用 `--model` 覆盖；图像适配器使用官方 Images API 的 `gpt-image-1`。生成主图仅作抽象图像，日期、文字、二维码仍由 HTML 排版。这里交付的示例全部是确定性模板，没有冒称 AI 生成图像。外部 API 的网络格式/错误分支有离线契约测试；未使用真实凭据执行付费调用。参见 [Provider 限制](docs/providers.md)。

## 输出与检查

```text
output/<slug>/
  poster_portrait.png       poster_square.png       invitation.png
  poster_print.pdf          invite_letter.pdf
  copy/{short.txt,social.md,formal.md,invitation.txt}
  event.json                manifest.json           preview.html
  *.html                    registration_qr.png     style_override.json
```

最后两个文件按需要产生。各 HTML 源可编辑；manifest 记录大小、哈希、尺寸、实际字体、文字边界、事实检查、评分/选择和二维码来源。打印版为 A4 RGB PDF，嵌入文字；不是印刷厂 CMYK/出血工艺文件。关键字段过长导致字号降到下限仍溢出会失败，不悄悄裁掉地点、日期或报名方式。

```sh
ruff check eventcraft scripts tests
python scripts/validate_skill.py
pytest -q
python -m build
```

[验收报告](docs/verification.md) 记录本机真实运行结果。CI 在 Ubuntu 配置 Noto CJK 并运行全部测试和无密钥烟测；远端 CI 需你发布后触发。

## Agent Skill 安装、隐私与发布

将项目目录作为 `eventcraft` Skill 安装/链接到客户端技能目录，安装其 Python CLI，然后调用 `$eventcraft`。 [安装和实际对话](docs/skill-usage.md)。不同 Agent 的文件/OCR/视觉能力不同；不假设所有客户端都有相同图像 API。

用户输入和 `output/` 默认不提交，`.env` 禁止跟踪。`--input-root` 限制输入路径和素材；文件、图片、DOCX/PDF 有大小上限。不会主动联网检查报名 URL，不将敏感数据写日志。参考研究没有下载或复制任何第三方素材；原创 SVG 和代码 MIT，依赖各自保留许可。 [第三方声明](THIRD_PARTY_NOTICES.md)

常见问题：无中文字体请安装系统 CJK；扫描 PDF 需 Agent 视觉或先转录；截图 OCR 需可选依赖和 Tesseract `chi_sim+eng`；数字选择错误先重新 recommend；原始文件有歧义请补充规范 JSON。

已准备本地仓库、MIT、CI、发布清单。**本次没有创建 GitHub 仓库或上传任何文件。** 由维护者按 [发布指南](docs/release.md) 自行发布。 [贡献规范](CONTRIBUTING.md) · [架构](docs/architecture.md) · [设计研究](docs/design-research.md)
