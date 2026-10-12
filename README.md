# EventCraft

**把活动资料变成一整套宣传物料：十套风格，智能三选一，确认后一次生成。**

[English](README.en.md) · [Releases](https://github.com/cagedb1rd/EventCraft/releases) · [Style Gallery](docs/style-gallery.md) · [Codex Skill 使用指南](docs/skill-usage.md) · [MIT License](LICENSE)

## 十套独立视觉设计系统

![十套风格实际生成海报](examples/visual-v3/style-gallery.png)

| ID | 风格 | 结构与适用场景 |
|---|---|---|
| swiss-grid | 瑞士网格设计 | 索引轴线、不对称网格；讲座、论坛 |
| editorial-minimal | 编辑杂志极简风 | 刊头、偏置构图、编辑留白；艺术、文化 |
| tech-gradient | 现代科技渐变风 | 活动主题相关的玻璃雕塑与光学结构、深色自然留白；科技、发布 |
| academic-clean | 学术专业风 | 主题相关的研究绘图、宋体层级与浅色留白；学术、培训 |
| neo-brutal | 年轻大胆风 | 实验拼贴、极粗标题与非对称构图；招新、市集 |
| retro-print | 复古印刷风 | 主题相关的版画与半调质感、复古标题；复古、音乐 |
| neon-night | 霓虹夜生活风 | 主题相关的舞台光线、克制发光标题；夜间音乐、派对 |
| warm-playful | 温暖手绘风 | 主题插画、楷体气质与温暖留白；生日、亲子 |
| luxury-elegant | 奢华典雅风 | 浮雕金箔 Art Deco、仪式中轴；婚礼、晚宴 |
| sports-dynamic | 运动竞技风 | 主题竞技元素、绘画动势与粗重斜体；体育、竞技 |

每套风格均有真实海报与邀请函：[完整 Style Gallery](examples/visual-v3/index.html) · [图片与 PDF 索引](docs/style-gallery.md)。海报默认仅含标题、一个简短且由用户提供的副标题、自然日期和地点；CTA／品牌按需要展示。文字融入预先设计的自然留白，不默认贴不透明底板。报名链接不强制生成二维码，只有明确扫码意图或 `qr_policy=show` 才加入。[标题长度压力测试](examples/visual-v3/title-gallery.png)

五套完整案例：[校园讲座](examples/generated/lecture/preview.html) · [科技发布](examples/generated/launch/preview.html) · [生日聚会](examples/generated/birthday/preview.html) · [典雅晚宴](examples/generated/dinner/preview.html) · [运动赛事](examples/generated/sports/preview.html)。GitHub 不会直接执行这些 HTML；下载后可离线打开，PNG 和 PDF 可直接查看。

```sh
eventcraft gallery --output output/gallery
# 以下是可重复的离线复用素材示例，不会调用宿主 ImageGen
python scripts/generate_examples.py
python scripts/generate_style_gallery.py
python scripts/build_title_showcase.py
```

## 项目简介

EventCraft 是一个可安装的 Agent Skill，也提供独立 Python CLI。Codex Agent 用内置 `image_gen` 创作主视觉，Chromium 精确排版中英文、日期、地点和二维码。无需 OpenAI API Key；CLI 离线预览可复用随包附带的原创素材，并如实记录素材来源。所有公开示例均为虚构 Demo。

当前源码版本 **1.1.0**：根据活动主题、标题长度和输出比例先规划构图，再生成原创主视觉；十套风格同时定义艺术媒介、中文／英文字体和排版策略。[视觉架构](docs/visual-architecture.md) · [验收记录](docs/verification-visual-v3.md) · [更新说明](docs/release-notes-1.1.0.md)。源码版本与已发布的 Release 可能不同，请核对下载附件的版本。

## 可以生成什么

![四种独立视觉邀请函](examples/visual-v3/invitation-gallery.png)

| 产物 | 格式 |
|---|---|
| 竖版主海报 | 1080 × 1920 PNG |
| 社交媒体方图 | 1080 × 1080 PNG |
| 视觉邀请函 | 登机牌 1600×800、票券 1600×700、正式卡 1080×1350、折页 1800×1000 PNG |
| 打印文件 | A4 海报/文字邀请函、邀请函原比例 PDF、折页封面与内页双页 PDF |
| 宣传文案 | 短文案、社媒帖、活动通知、邀请文字 |
| 可编辑与可核验文件 | HTML 源、event.json、manifest.json、离线预览页 |

- 从十套设计中推荐三个选项，附真实预览、推荐依据和取舍。
- 支持选择、自动选择、换一批、直接指定风格，以及保存和恢复选择状态。
- 海报、邀请函与文案读取同一份活动事实，缺失必填信息时集中确认。
- 支持 Logo、主图、讲者照片、原始二维码和参考图片；标题按实际字宽自适应排版。

## 下载与版本

- **源码和完整示例**：克隆本仓库，或点击 **Code → Download ZIP**。
- **可安装 Skill ZIP**：查看 [Releases](https://github.com/cagedb1rd/EventCraft/releases)，选择维护者上传的 `eventcraft-skill-1.1.0.zip` 附件。默认精简包包含 `SKILL.md`、运行代码、十套原创预览素材、设计指南和输入样例；完整成品 Gallery 在源码中，或用 `--with-examples` 另行打包。GitHub 自动生成的 **Source code (zip)** 是源码快照。若 Release 尚无附件，可按下文从源码打包。
- **Python CLI**：Release 中的 `.whl` / `.tar.gz` 用于 Python 安装；只安装 wheel 不会注册 Codex Skill。

Skill ZIP 不包含 Python 虚拟环境、Chromium、系统字体或 API 凭据，安装后仍需配置运行依赖。

## 安装与第一次生成

需要 **Python 3.11+、Chromium 和中文字体**。Windows 通常已有 Microsoft YaHei / SimSun；macOS 使用系统中文字体；Linux 建议安装 Noto CJK。系统字体不随仓库分发。

在本仓库点击 **Code → Download ZIP** 并解压，或复制仓库地址执行：

```sh
git clone https://github.com/cagedb1rd/EventCraft.git eventcraft
cd eventcraft
```

本项目仓库为 `cagedb1rd/EventCraft`。以下命令均在包含 `pyproject.toml` 和 `SKILL.md` 的项目根目录运行。

### Windows PowerShell

无需激活虚拟环境，直接使用其中的可执行文件：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\eventcraft.exe all examples/inputs/lecture.json --auto-style --output output/lecture
Start-Process .\output\lecture\preview.html
```

### macOS / Linux

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m playwright install chromium
eventcraft all examples/inputs/lecture.json --auto-style --output output/lecture
```

这组 CLI 命令是复用随包原创素材的离线烟测，并未调用 ImageGen。新活动的原创视觉请使用下文 Codex Skill 工作流。在浏览器打开 `output/lecture/preview.html` 查看全部成品。安装依赖和浏览器需要网络；复用原创素材的渲染完全在本地执行。定制主视觉由 Codex 内置工具生成，再通过下文的素材桥接导入。Windows 可回退到已安装的 Chrome/Edge，也可通过 `EVENTCRAFT_BROWSER` 指定浏览器可执行文件。

**下文 CLI 示例中的 `eventcraft`：Windows 请使用 `.\.venv\Scripts\eventcraft.exe`；macOS/Linux 在已激活的虚拟环境中直接使用。脚本示例中的 `python` 同样应使用项目虚拟环境。**

## 在 Codex 中使用

先完成上面的 Python 依赖安装，再安装完整 Skill。Skill 包含运行代码、配置、设计规范和资源，不能只复制 `SKILL.md`。

将 Release 下载的完整 Skill ZIP 放入项目 `dist/`；没有下载包时运行下面的打包命令。已有 ZIP 时跳过该命令，其余安装步骤相同。

Windows PowerShell：

```powershell
# 已下载完整 Skill ZIP 时跳过下一行
.\.venv\Scripts\python.exe scripts/package_skill.py
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills" | Out-Null
Expand-Archive -LiteralPath ".\dist\eventcraft-skill-1.1.0.zip" -DestinationPath "$env:USERPROFILE\.agents\skills"
```

macOS/Linux，在已激活的虚拟环境中：

```sh
# 已下载完整 Skill ZIP 时跳过下一行
python scripts/package_skill.py
mkdir -p "$HOME/.agents/skills"
unzip dist/eventcraft-skill-1.1.0.zip -d "$HOME/.agents/skills"
```

安装后应存在 `~/.agents/skills/eventcraft/SKILL.md`。这些命令用于首次安装；已有同名技能时，请先按[使用指南](docs/skill-usage.md)检查和更新。Codex 支持该用户技能目录；若安装后未出现，重启 Codex。[官方技能说明](https://learn.chatgpt.com/docs/build-skills)

在 Codex 打开项目目录，发送：

```text
使用 $eventcraft。
读取 examples/inputs/lecture.json，这是演示活动。
先推荐三种风格并展示真实预览，我选择后再生成整套物料。
运行 CLI 时使用当前项目的 .venv 虚拟环境。
```

看到预览后可回复“选第二个”“换一批”“自动选最优”或指定风格。创建自己的活动时，直接提供活动文字或附件；Agent 会确认必要事实，再推荐和生成。也可以不全局安装，在项目聊天里明确要求 Codex 阅读根目录的 `SKILL.md` 并按其流程执行。

## CLI：推荐、选择与自己的活动

```sh
# 生成三个真实预览
eventcraft recommend examples/inputs/lecture.json --output output/selection
# 打开 output/selection/recommendations.html 后，选择第二项
eventcraft all examples/inputs/lecture.json --select 2 --state output/selection --output output/chosen
# 换一批，不重复当前选项
eventcraft recommend examples/inputs/lecture.json --output output/selection --next
# 直接指定任意内置风格
eventcraft render examples/inputs/lecture.json --style retro-print --output output/retro
```

推荐结果与当前编号保存在选择目录中。活动资料修改后，旧编号选择会失效，需要重新推荐。默认展示三个选项；主动传入 `--all` 才展示全部。评分为可解释的工程规则，支持品牌禁止色/风格等硬约束及自定义权重。[推荐算法](docs/style-recommendation.md) · [真实 CLI 运行记录](docs/recommendation-terminal.txt)

自己的资料建议放在已被 Git 忽略的 `private/` 中。可以参考 [JSON 样例](examples/inputs/lecture.json) 和[数据契约](references/event-schema.md)，提供真实标题、日期、时间、IANA 时区、地点或线上平台、报名方式。删除不适用的示例字段，替换 `example.org` 链接；正式活动将 `demo` 设为 `false`。

```sh
eventcraft all private/event.json --auto-style --output output/my-event
# 从已有文档抽取资料，并集中补充缺失信息
eventcraft extract examples/inputs/lecture.md --output output/extracted/event.json
eventcraft all examples/inputs/lecture.md --interactive --output output/interactive
```

支持 JSON、文本、Markdown、TXT、DOCX、带文本层 PDF，以及可选 Tesseract OCR 截图。无模型的抽取采用字段标签和保守正则；隐含信息与冲突需要确认。`--draft` 允许生成明确标记的草稿。中文默认，`--language en` 使用英文标签与文案；`bilingual` 接受用户提供的中英混排内容，活动事实不会自动翻译。

## 内置图像生成与参考图

默认 Skill 工作流由 Agent 实际调用内置 `image_gen`，再导入真实图片。Python CLI 不会冒充宿主工具。示例流程：

```sh
eventcraft art-plan examples/inputs/web-summit.json --style tech-gradient --output output/art-plan.json
# Codex 读取 plan.prompt，实际调用 image_gen 并检查返回的图片。
eventcraft art-import output/art-plan.json --image <真实生成图片路径> --output output/art-v1
eventcraft all examples/inputs/web-summit.json --style tech-gradient --visual-receipt output/art-v1/receipt.json --require-art --output output/web-summit
```

每个新活动应重新构思并实际生成，不能复用 Gallery 背景只换文字。生成前计划包含自然文字区和字体契约；方图／A4 需要不同留白时使用 `art-plan --ratio square` 或 `--ratio print`，将导入凭据保存到 `assets.visual_variants`。

`--require-art` 禁止静默替换为内置复用图；receipt 校验活动事实、风格和文件哈希。宿主没有图像生成能力时，Agent 明确说明限制。完整安装包保留此流程。[素材桥接](references/image-generation.md) · [同风格不同主题](examples/visual-v3/dynamic-comparison.png) · [隔离 Skill 实际成品](examples/visual-v3/installed-runtime/preview.html)

```sh
eventcraft render examples/inputs/dinner.json --style luxury-elegant --style-reference examples/inputs/palette.png --style-description '奢华典雅风，细线与留白' --output output/custom
```

参考图片最多五张。CLI 离线分析只提取颜色；Codex Agent 需要实际查看参考图，理解构图、材质与设计语言后创作原创主视觉。`style_override.json` 保存可重放的设计参数与参考哈希，参考原图不会嵌入成品。用户 Logo/照片保留比例，原始二维码保留内容；明确扫码意图或 `qr_policy=show` 时才从有效 URL 生成二维码；`hide` 可关闭，无二维码不留占位。

可选官方 OpenAI Provider 支持资料理解、参考图视觉分析和抽象主图生成，需要 `OPENAI_API_KEY` 环境变量及显式 `--allow-network`，可能产生 API 费用。

```sh
eventcraft extract examples/inputs/lecture.md --llm --allow-network --output output/model-event.json
eventcraft render examples/inputs/dinner.json --style-reference examples/inputs/palette.png --vision --allow-network --output output/vision
eventcraft render examples/inputs/launch.json --auto-style --generate-hero 'Original abstract orbital sculpture, no text' --allow-network --output output/with-art
```

模板示例不依赖付费 API。外部请求格式与错误分支有离线契约测试，真实付费调用尚未验证。配置与支持范围见 [Provider 文档](docs/providers.md)。

## 输出与质量检查

```text
output/<activity>/
├── poster_portrait.png、poster_square.png、invitation.png
├── poster_print.pdf、invitation_print.pdf、invite_letter.pdf
├── invitation_outside.png、invitation_folded_print.pdf  # 折页形式
├── copy/
│   └── short.txt、social.md、formal.md、invitation.txt
├── event.json、manifest.json、preview.html
├── *.html
└── registration_qr.png、style_override.json  # 按需要生成
```

manifest 记录文件哈希、尺寸、实际字体、标题布局/行数、文字边界、事实检查和选择状态。检查覆盖文字越界、模块重叠、图片加载、PDF 页面与对比度。长内容达到最小字号仍放不下时会明确报错。

[视觉验收](docs/verification-visual-v3.md)记录 15 次真实 ImageGen 调用、16 套物料和 60 个 PDF／66 页检查。完整回归 111 项通过；随后 23 项相关回归及 6 项最终契约通过，这些不是同一次全套运行。[历史验收](docs/verification.md)保留旧结果。跨平台、真实 OCR 与付费 API 未重新验收；远程 CI 以当前提交实际运行结果为准。

## 隐私、限制与常见问题

- 基础渲染不联网加载素材。`private/`、`output/` 和 `.env` 被 Git 忽略；自己新建的其他资料路径需自行检查是否会被提交。
- `--input-root` 可以限制资料与素材路径；图片和文档有大小上限。报名 URL 只做语法验证，不自动检查业务有效性。
- 扫描 PDF 需要 Agent 视觉或先转录；截图 OCR 需要可选依赖及 Tesseract 的 `chi_sim+eng` 语言包，本机 OCR 验收尚未完成。
- 中文显示异常时安装可用的 CJK 字体。不同平台字体回退会改变字形和换行。
- A4 PDF 是 RGB 浏览器打印文件，保留矢量文字；不提供印刷厂 CMYK、出血和色彩校准。
- 编号选择失效时重新运行 `recommend`。原资料有歧义时，补充规范 JSON 或使用 Agent 集中确认。

## 开发与贡献

```sh
python -m pip install -e '.[dev]'
python -m ruff check eventcraft scripts tests
python scripts/validate_skill.py
python -m pytest -q
python -m build
```

GitHub Actions 在 push/PR 时运行 lint、Skill 校验、测试、无密钥生成烟测和构建。精确开发依赖见 `requirements-dev.lock`。[贡献指南](CONTRIBUTING.md) · [架构](docs/architecture.md) · [设计系统](docs/design-system.md) · [设计研究](docs/design-research.md) · [维护者发布指南](docs/release.md)

代码与原创图形采用 [MIT License](LICENSE)。系统字体和第三方艺术素材不随项目分发；依赖保留各自许可证。[第三方声明](THIRD_PARTY_NOTICES.md)
