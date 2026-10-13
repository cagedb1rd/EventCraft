# EventCraft 使用指南 / Usage guide

首次使用请按 [中文 README](../README.md#第一次使用) 或 [English README](../README.en.md#first-time-setup) 操作。完整 Skill ZIP 包含指令、运行代码、设计配置和十套原创预览素材。它不包含 Python 环境、Chromium、系统字体、开发脚本或测试。

## 安装与更新

从 [最新 Release](https://github.com/cagedb1rd/EventCraft/releases/latest) 下载 `eventcraft-skill-版本号.zip`。将外层 `eventcraft/` 文件夹放入 `~/.agents/skills/`；Windows 对应 `%USERPROFILE%\.agents\skills\`。最终必须存在 `eventcraft/SKILL.md` 和全部支持文件。

在该目录创建 `.venv`，用其中的 Python 执行 `-m pip install -e .` 和 `-m playwright install chromium`，然后检查中文字体。安装指令不会自动安装这些依赖。[官方 Skill 目录与调用说明](https://learn.chatgpt.com/docs/build-skills)

更新时先备份个人修改，再替换完整目录、重新安装当前 Python 包；不要仅覆盖 `SKILL.md`，也不要在用户目录和项目目录各安装一份同名 Skill。新聊天选择 EventCraft；CLI / IDE 可用 `$eventcraft`。未出现时检查目录或重启 Codex。

## 一次完整活动流程

1. 提供活动文字或附件：标题、完整日期/时间、时区、地点、报名方式、受众和素材。Agent 提取并集中确认缺失或冲突。
2. 展示三款真实推荐预览。这一步复用随包原创素材，不声称已经创作本次活动图片。
3. 回复编号、自动选择、换一批、风格名或提供参考图。Agent 保留选择状态。
4. Agent 为你的活动规划构图，实际调用内置图像工具，查看结果并导入生成的图片。
5. 使用同一份活动事实导出海报、视觉邀请函、打印 PDF、文案和可编辑 HTML，检查成品并返回 `preview.html` 路径。

活动输出保存到你指定的项目目录。安装 Skill 的目录用于运行工具，不必成为活动资料的存放位置。提示 Agent 使用已安装 Skill 的 `.venv` 和绝对路径，避免调用另一份旧 CLI。

没有内置图像工具时会说明限制。素材复用需要如实说明；不会自动转向付费 API。截图读取取决于宿主视觉能力，CLI 可选 OCR 需要另行安装 Tesseract。不要把隐含信息当作已确认事实。

## 命令行示例

以下命令在 Skill / 源码根目录运行。Windows 将 `eventcraft` 替换为 `.\.venv\Scripts\eventcraft.exe`，macOS / Linux 使用 `.venv/bin/eventcraft`。

```sh
# 三款实际预览，状态存到独立目录
eventcraft recommend examples/inputs/lecture.json --output output/selection
# 当前列表的第二款，复用随包素材做离线示例
eventcraft all examples/inputs/lecture.json --select 2 --state output/selection --output output/chosen
# 换一批
eventcraft recommend examples/inputs/lecture.json --output output/selection --next
# 自动选最优
eventcraft all examples/inputs/lecture.json --auto-style --output output/auto
```

这些离线命令不调用聊天图像工具。真正的新活动由 Agent 编排；素材计划、真实调用、导入和 `--require-art` 流程见 [图像生成桥接](../references/image-generation.md)。活动事实改变后需重新推荐，旧编号不能继续使用。

自己的资料放入 `private/`，参考 [JSON 样例](../examples/inputs/lecture.json) 和 [数据契约](../references/event-schema.md)，替换所有虚构内容和 `example.org` 链接；正式活动设置 `demo=false`。`--draft` 只适用于明确要求的草稿。

```sh
# 导出当前安装版本支持的参数
eventcraft --help
eventcraft all --help
# 直接指定风格并指定邀请函形式
eventcraft all private/event.json --style retro-print --invitation-format ticket-stub --output output/my-event
```

上述最后一条仍是 CLI 素材复用路径；加入真实生成的 `--visual-receipt` 和 `--require-art` 才会强制使用导入图片。

## 结果与选项

- `preview.html`：离线查看全部成品；HTML 可编辑，PNG 分享，PDF 打印。
- `event.json`：同一份活动事实；`manifest.json`：尺寸、字体、布局、素材来源和哈希记录。
- `qr_policy=auto` 仅在明确扫码意图时生成；`show` 要求有效链接，`hide` 隐藏。
- `--invitation-format` 支持 `boarding-pass`、`ticket-stub`、`formal-card`、`folded`。
- 中文为默认；`--language en` 用于英文标签/文案，`bilingual` 接受已提供的混排内容，不自动翻译事实。
- 原创主视觉由宿主 Agent 创建；Python API 适配器是可选的明确授权路径，不是默认。

## 从源码开发

```sh
git clone --depth 1 https://github.com/cagedb1rd/EventCraft.git
cd EventCraft
```

按 [开发指南](../CONTRIBUTING.md) 安装开发依赖和运行检查；`python scripts/package_skill.py` 构建默认用户包。`--with-examples` 是可选开发资料包。旧生成 Gallery 和全部验收输出位于 [v1.1.0 历史快照](https://github.com/cagedb1rd/EventCraft/tree/v1.1.0)。用户安装无需克隆完整 Git 历史。
