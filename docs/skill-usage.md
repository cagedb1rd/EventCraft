# Agent Skill use

The repository root is the skill folder: `SKILL.md`, `agents/openai.yaml`, scripts, references and assets belong together. Install its CLI with `python -m pip install -e <absolute-repository-path>`. Install Chromium and system CJK fonts. A wheel alone installs the CLI; Agent instructions are in the repository/skill archive.

For Codex, put the complete skill folder at `~/.agents/skills/eventcraft` (Windows: `%USERPROFILE%\.agents\skills\eventcraft`). Codex also discovers repository skills under `.agents/skills`, and supports symlinked skill folders. A root-level `SKILL.md` alone does not register the project as an installed skill. See [official skill discovery documentation](https://learn.chatgpt.com/docs/build-skills). Codex detects changes automatically; restart Codex if the skill does not appear. This work created the skill in the project; it did not alter the user's global skill installation.

A complete skill archive is built by `python scripts/package_skill.py`; it includes public fictional examples and excludes `.venv`, Git metadata and user output. On this Windows checkout, install the built archive with:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills" | Out-Null
Expand-Archive -LiteralPath "D:\project\eventCraft\dist\eventcraft-skill-1.0.0.zip" -DestinationPath "$env:USERPROFILE\.agents\skills"
```

The ZIP contains the outer `eventcraft/` directory. The final path must be `%USERPROFILE%\.agents\skills\eventcraft\SKILL.md`, with its supporting files alongside it. These commands do not replace an existing skill folder. Installing the instructions does not install Python dependencies: use the existing project virtual environment or install the CLI separately.

In the current project, no global installation is necessary to follow the workflow explicitly. Ask Codex to read `D:\project\eventCraft\SKILL.md` and use `D:\project\eventCraft\.venv\Scripts\eventcraft.exe`. Once registered, start a chat for `D:\project\eventCraft`, invoke `$eventcraft`, provide the activity facts, and specify the project virtual-environment executable if it is not on PATH.

Suggested conversation:

> 使用 $eventcraft。2026 年 10 月 26 日 14:00–16:30，Asia/Shanghai，示例大学创新楼报告厅，举办 AI Agent 实战分享会，面向学生和开发者，免费，报名链接 https://example.org/events/agent-lab。活动为 Demo。先推荐三种风格。

The Agent normalizes these facts with evidence, runs `recommend`, displays three actual preview PNGs and reasons. A reply “2” maps to current state; `all --select 2 --state <dir>` generates the whole campaign. “自动选最优” uses `--auto-style`; “换一批” uses `recommend --next`; “复古印刷风” uses `--style retro-print`; a reference image skips style interaction and uses `--style-reference`.

If the user omitted a year, time, timezone, usable venue or registration method, the Agent asks once with a combined question before preview/finished material selection. It does not invent a school, speaker, fee, award or organizer. When host vision is available, the Agent may analyze an attached screenshot within its authorization and write validated facts, preserving source confidence and unknowns. The CLI's plain extraction is deliberately narrower.

The CLI's offline copy is conservative fact-based text. The Agent may refine it with natural-language ability while keeping dates/time/venue/registration identical to `event.json`; verify final prose. Host capabilities and model APIs vary by client. Optional APIs are never assumed to be installed or authorized.

State and output remain in local project directories. The skill should show real artifacts and manifest results, report drafts, palette-only limitations and unverified external capabilities. It does not autonomously publish user materials or GitHub repositories.
