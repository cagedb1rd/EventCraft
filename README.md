# EventCraft

**AI 海报生成与活动物料 Skill：十套独立视觉设计系统，一次生成海报、邀请函和宣传文案。**

[English](README.en.md) · [下载 Skill](https://github.com/cagedb1rd/EventCraft/releases/latest) · [更多效果](docs/style-gallery.md) · [详细使用指南](docs/skill-usage.md)

## 十套独立视觉设计系统

![十套独立视觉设计系统的真实海报](examples/visual-v3/style-gallery.png)

每套系统都有独立的艺术媒介、字体层级和构图策略。新活动由 Codex 的内置图像工具创作专属主视觉，再由本地渲染器准确排入中英文、日期和地点。三款初始推荐预览使用随包原创素材；选定风格后才创作本次活动的图片。

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

## 先看能拿到什么

![四种独立视觉邀请函](examples/visual-v3/invitation-gallery.png)

| 成品 | 内容 |
|---|---|
| 海报 | 竖版 1080×1920、社媒方图 1080×1080、A4 打印 PDF |
| 视觉邀请函 | 登机牌、票券、正式卡或折页；PNG 和原比例 PDF |
| 宣传文案 | 短文案、社媒帖、活动通知和邀请文字 |
| 可编辑文件 | HTML、活动数据、离线预览页和生成记录 |

海报保留核心信息，二维码按需生成。折页附内外展开图和双页 PDF。[查看单张海报和打印示例](docs/style-gallery.md)。公开展示均为虚构 Demo。

## 第一次使用

需要能读写本地文件、执行 Python 的 Codex，以及 **Python 3.11+、Chromium 和中文字体**。原创主视觉还需要当前聊天提供内置图像生成工具。无需 OpenAI API Key；没有该工具时，Agent 会说明限制，可在你接受后使用随包素材。

### 1. 下载并放好完整 Skill

打开 [最新 Release](https://github.com/cagedb1rd/EventCraft/releases/latest)，下载 **`eventcraft-skill-版本号.zip`**，不要选择 GitHub 自动生成的 Source code ZIP。

将 ZIP 内的整个 `eventcraft` 文件夹解压到：

| 系统 | 最终文件路径 |
|---|---|
| Windows | `%USERPROFILE%\.agents\skills\eventcraft\SKILL.md` |
| macOS / Linux | `~/.agents/skills/eventcraft/SKILL.md` |

保留同目录下的全部文件，不能只复制 `SKILL.md`。这是 Codex 的用户级 Skill 目录，[官方目录说明](https://learn.chatgpt.com/docs/build-skills)。已有安装时先备份个人修改，再替换完整文件夹。

### 2. 安装运行依赖（只需做一次）

在 Codex 中打开解压后的 `eventcraft` 文件夹，发送：

```text
请为这个 EventCraft Skill 配置本地运行环境：
检查 Python 3.11+，在 Skill 文件夹创建 .venv，
用该虚拟环境安装当前目录的 Python 包和 Playwright Chromium，
检查中文字体，然后用 examples/inputs/lecture.json 做一次离线示例导出。
告诉我预览文件的路径。这一步使用随包素材，不调用图像生成。
```

如果希望自己执行命令，展开下面对应系统的步骤。依赖与浏览器的首次下载需要联网。

<details>
<summary>Windows PowerShell</summary>

在解压后的 Skill 文件夹打开 PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\eventcraft.exe all examples/inputs/lecture.json --auto-style --output output/demo
Start-Process .\output\demo\preview.html
```

Windows 通常已有 Microsoft YaHei / SimSun。安装包不附带系统字体。

</details>

<details>
<summary>macOS / Linux</summary>

在解压后的 Skill 文件夹打开终端：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m playwright install chromium
.venv/bin/eventcraft all examples/inputs/lecture.json --auto-style --output output/demo
```

打开 `output/demo/preview.html`。macOS 使用系统中文字体；Ubuntu / Debian 可通过 `sudo apt-get install fonts-noto-cjk` 安装中文字体。Linux 缺少浏览器依赖时运行 `.venv/bin/python -m playwright install --with-deps chromium`。

</details>

### 3. 给 Codex 活动资料

在你的活动项目里打开新聊天，选择 EventCraft Skill，或明确说“使用 EventCraft”。CLI / IDE 中可用 `$eventcraft`。如果未出现，重启 Codex 并检查上面的最终路径。

直接粘贴活动的原始文字描述，或附上 **Word、带文本层的 PDF、Markdown** 文件，再发一句：

```text
使用 EventCraft，根据这份活动资料制作海报、邀请函和宣传文案，先推荐三种风格。
```

Skill 会自动读取资料、提取活动信息并整理成可用于生成的数据。资料完整时直接展示三款预览；只有关键内容缺失或存在冲突时，才集中补问必要信息。无需自己提取字段、填写表格或指定 CLI 命令。

有 Logo、照片或参考图也可以一起附上；风格和邀请函形式可以用自然语言提出。

### 4. 选风格，查看成品

看到三款预览后，回复 **“选第二个”**、**“换一批”**、**“自动选最优”**，或指定某套风格。也可指定“邀请函做成票券”并提供参考图片。

选定后，Agent 创建原创主视觉、检查图片，再一次导出整套物料。打开它返回的 `preview.html` 查看结果；PNG 可分享，PDF 可打印，HTML 可继续调整。自己的成品保存在本地输出目录，不会自动上传。

## 常见问题

| 问题 | 怎么处理 |
|---|---|
| Skill 看不到 | 检查最终路径和 `SKILL.md`，避免多套一层目录；必要时重启 Codex |
| `eventcraft` 命令找不到 | 让 Agent 使用已安装 Skill 的 `.venv`；Windows 可执行文件在 `.venv/Scripts/` |
| 标题缺字或中文不对 | 安装中文字体后重新生成；系统字体不随包分发 |
| 没有图像生成工具 | 不会自动转付费 API；Agent 会说明可用的素材复用方式 |
| 不确定下载哪个文件 | 只需完整 Skill ZIP；SHA256SUMS 用于校验，不需要 Python wheel |

## 命令行与开发

只使用命令行、想从源码安装或参与开发，请看 [详细使用指南](docs/skill-usage.md)、[开发指南](CONTRIBUTING.md) 和[架构](docs/architecture.md)。CLI 能渲染随包素材和导入的图片；聊天内的原创图像生成由 Codex Agent 编排。

仓库保留运行代码、十套原创预览素材、输入样例、精简效果展示和自动化测试。**测试用于 GitHub CI，用户安装包不包含测试、开发脚本或历史输出。** 旧版本的完整验收产物可在 [v1.1.0 源码快照](https://github.com/cagedb1rd/EventCraft/tree/v1.1.0) 中查看。

[MIT License](LICENSE) · [第三方说明](THIRD_PARTY_NOTICES.md) · [验证记录](docs/verification-visual-v3.md)
