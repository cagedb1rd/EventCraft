# Agent Skill use

The repository root is the skill folder: `SKILL.md`, `agents/openai.yaml`, scripts, references and assets belong together. Install its CLI with `python -m pip install -e <absolute-repository-path>`. Install Chromium and system CJK fonts. A wheel alone installs the CLI; Agent instructions are in the repository/skill archive.

For Codex, put the complete skill folder at `~/.agents/skills/eventcraft` (Windows: `%USERPROFILE%\.agents\skills\eventcraft`). Codex also discovers repository skills under `.agents/skills`, and supports symlinked skill folders. A root-level `SKILL.md` alone does not register the project as an installed skill. See [official skill discovery documentation](https://learn.chatgpt.com/docs/build-skills). Codex detects changes automatically; restart Codex if the skill does not appear.

A complete skill archive is built by `python scripts/package_skill.py`; it includes public fictional examples and excludes `.venv`, Git metadata and user output. From the repository root on Windows, install dependencies as described in the README, then run:

```powershell
.\.venv\Scripts\python.exe scripts/package_skill.py
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills" | Out-Null
Expand-Archive -LiteralPath ".\dist\eventcraft-skill-1.0.0.zip" -DestinationPath "$env:USERPROFILE\.agents\skills"
```

On macOS/Linux, activate the repository's virtual environment and run:

```sh
python scripts/package_skill.py
mkdir -p "$HOME/.agents/skills"
unzip dist/eventcraft-skill-1.0.0.zip -d "$HOME/.agents/skills"
```

The ZIP contains the outer `eventcraft/` directory. The final path must be `~/.agents/skills/eventcraft/SKILL.md`, with its supporting files alongside it. These commands are for first-time installation. Before updating an existing skill, inspect its contents and preserve any personal changes; replacing an installed copy is a separate maintainer action. Do not install duplicate copies with the same skill name at user and repository scope. Installing the instructions does not install Python dependencies: use the project virtual environment or install the CLI separately.

Without global installation, ask Codex in a project chat to read the root `SKILL.md` and follow its workflow. Once registered, open the repository directory in Codex and invoke `$eventcraft`. Specify the project's virtual environment when the CLI is not on PATH: `.venv\Scripts\eventcraft.exe` on Windows or `.venv/bin/eventcraft` on macOS/Linux. An installed Skill is not a Python runtime; its scripts still need the dependencies from `pyproject.toml`.

Suggested conversation:

> 使用 $eventcraft。2026 年 10 月 26 日 14:00–16:30，Asia/Shanghai，示例大学创新楼报告厅，举办 AI Agent 实战分享会，面向学生和开发者，免费，报名链接 https://example.org/events/agent-lab。活动为 Demo。先推荐三种风格。

The Agent normalizes these facts with evidence, runs `recommend`, displays three actual preview PNGs and reasons. A reply “2” maps to current state; `all --select 2 --state <dir>` generates the whole campaign. “自动选最优” uses `--auto-style`; “换一批” uses `recommend --next`; “复古印刷风” uses `--style retro-print`; a reference image skips style interaction and uses `--style-reference`.

If the user omitted a year, time, timezone, usable venue or registration method, the Agent asks once with a combined question before preview/finished material selection. It does not invent a school, speaker, fee, award or organizer. When host vision is available, the Agent may analyze an attached screenshot within its authorization and write validated facts, preserving source confidence and unknowns. The CLI's plain extraction is deliberately narrower.

The CLI's offline copy is conservative fact-based text. The Agent may refine it with natural-language ability while keeping dates/time/venue/registration identical to `event.json`; verify final prose. Host capabilities and model APIs vary by client. Optional APIs are never assumed to be installed or authorized.

State and output remain in local project directories. The skill should show real artifacts and manifest results, report drafts, palette-only limitations and unverified external capabilities. It does not autonomously publish user materials or GitHub repositories.
