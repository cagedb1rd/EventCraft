# EventCraft

**An AI poster and event campaign Skill: ten independent visual design systems, with posters, invitations, and promotional copy in one export.**

[中文](README.md) · [Download Skill](https://github.com/cagedb1rd/EventCraft/releases/latest) · [Gallery](docs/style-gallery.md) · [Detailed guide](docs/skill-usage.md)

## Ten independent visual design systems

![Ten actual poster designs](examples/visual-v3/style-gallery.png)

Each system defines its artistic medium, typography, and composition. Codex creates artwork for your event, then the local renderer adds exact Chinese/English lettering, dates, and venues. Initial style previews use bundled original artwork; fresh artwork is created after you choose a style.

| ID | Style | Structure and use |
|---|---|---|
| swiss-grid | Swiss grid | Index axis, asymmetric grid; lectures and forums |
| editorial-minimal | Editorial minimal | Masthead, offset composition, whitespace; art and culture |
| tech-gradient | Tech gradient | Event-relevant glass sculpture and optical structures, natural dark space; technology |
| academic-clean | Academic professional | Event-relevant research drawings, serif hierarchy and pale space; research |
| neo-brutal | Neo brutalism | Experimental collage, heavy type and asymmetry; recruitment and markets |
| retro-print | Retro print | Event-relevant print imagery, letterpress texture and retro type; music |
| neon-night | Neon nightlife | Event-relevant stage lighting and restrained luminous type; nightlife |
| warm-playful | Warm illustrated | Thematic illustration, native handwritten character and warm space; families |
| luxury-elegant | Luxury elegant | Embossed Art Deco foil, ceremonial axis; weddings and dinners |
| sports-dynamic | Sports dynamic | Relevant competitive elements, painted movement and heavy italic type; sports |

## What you get

![Four visual invitation formats](examples/visual-v3/invitation-gallery.png)

| Deliverable | Contents |
|---|---|
| Posters | 1080×1920 portrait, 1080×1080 social square, A4 print PDF |
| Visual invitation | Boarding pass, ticket stub, formal card, or folded invitation; PNG and native-ratio PDF |
| Copy | Short copy, social post, event notice, and invitation text |
| Editable files | HTML, event data, offline preview, and generation records |

Posters focus on core facts; QR codes are optional. Folded invitations include exterior/interior artwork and a two-page PDF. [See individual designs and print samples](docs/style-gallery.md). All public examples are fictional Demos.

## First-time setup

Use Codex with local file and Python execution access, **Python 3.11+, Chromium, and CJK fonts**. Fresh artwork also requires a built-in image generation tool in your current chat. No OpenAI API key is required. If the tool is unavailable, the Agent explains the limitation and can reuse bundled artwork with your acceptance.

### 1. Download the complete Skill

Open the [latest Release](https://github.com/cagedb1rd/EventCraft/releases/latest) and download **`eventcraft-skill-VERSION.zip`**, rather than GitHub's automatic Source code archive.

Extract its entire `eventcraft` folder into your user skills directory:

| System | Final manifest path |
|---|---|
| Windows | `%USERPROFILE%\.agents\skills\eventcraft\SKILL.md` |
| macOS / Linux | `~/.agents/skills/eventcraft/SKILL.md` |

Keep all supporting files beside `SKILL.md`. See [official skill discovery documentation](https://learn.chatgpt.com/docs/build-skills). Back up personal changes before replacing an existing installation.

### 2. Install runtime dependencies once

Open the extracted `eventcraft` folder in Codex and send:

```text
Set up this EventCraft Skill locally.
Check Python 3.11+, create .venv inside the Skill folder,
install the current Python package and Playwright Chromium using that environment,
and check CJK fonts. Export examples/inputs/lecture.json as an offline smoke demo.
Return the preview path. Use bundled artwork for this setup check, without image generation.
```

Or run the commands yourself. Initial dependency and browser downloads require network access.

<details>
<summary>Windows PowerShell</summary>

Run inside the extracted Skill folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\eventcraft.exe all examples/inputs/lecture.json --auto-style --output output/demo
Start-Process .\output\demo\preview.html
```

Windows usually provides Microsoft YaHei / SimSun. System fonts are not bundled.

</details>

<details>
<summary>macOS / Linux</summary>

Run inside the extracted Skill folder:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m playwright install chromium
.venv/bin/eventcraft all examples/inputs/lecture.json --auto-style --output output/demo
```

Open `output/demo/preview.html`. macOS provides system CJK fonts. On Ubuntu / Debian, install them with `sudo apt-get install fonts-noto-cjk`. If browser libraries are missing on Linux, run `.venv/bin/python -m playwright install --with-deps chromium`.

</details>

### 3. Give Codex your event brief

Start a chat in your event project and select the Skill, or explicitly ask to use EventCraft. In the CLI / IDE, use `$eventcraft`. If it does not appear, check the final path above and restart Codex if needed.

Replace every bracketed field below; write “none” where appropriate:

```text
Use EventCraft to create posters, an invitation, and copy for my event.
Title: [event name]
Date and time: [full date, start and end times]
Timezone: [IANA timezone, e.g. Asia/Shanghai]
Venue: [address or online platform]
Registration: [URL, contact details, or no registration required]
Audience and theme: [who it is for and what it covers]
Assets: [attached logo, photos, references, or none]

Confirm missing facts together, then show three real style previews.
After I choose, use built-in image generation for this event's original artwork
and export the complete campaign. Run the CLI through the installed Skill's .venv.
Save the campaign to this project's output/my-event directory.
```

You can also attach Word, text-layer PDF, Markdown, or event text. The Agent extracts facts and asks about conflicts instead of inventing dates, venues, or registration details.

### 4. Choose a style and view the results

Reply **“option 2”**, **“another batch”**, **“choose automatically”**, or name a style. You can also request a ticket invitation or supply visual references.

The Agent creates and inspects original artwork, then exports the campaign. Open the returned `preview.html`; share the PNGs, print the PDFs, or edit the HTML. Your campaign stays in the local output directory and is not automatically published.

## Troubleshooting

| Issue | Action |
|---|---|
| Skill is missing | Check `SKILL.md` and the final path; avoid an extra nested folder and restart if needed |
| Command is missing | Use the installed Skill's `.venv`; Windows executables are under `.venv/Scripts/` |
| Missing Chinese glyphs | Install CJK fonts and regenerate |
| No image generation tool | The Agent explains reuse options; it does not silently use a paid API |
| Which asset to download? | The complete Skill ZIP; SHA256SUMS is optional verification, and a wheel is unnecessary |

## CLI and development

See the [detailed guide](docs/skill-usage.md), [contributing guide](CONTRIBUTING.md), and [architecture](docs/architecture.md) for source installation and CLI workflows. Python renders bundled/imported images; the Codex Agent orchestrates chat image generation.

The repository keeps runtime code, ten original preview assets, input samples, a compact gallery, and automated tests. **Tests serve GitHub CI; the default user archive excludes tests, development scripts, and historical outputs.** Complete earlier acceptance artifacts remain in the [v1.1.0 source snapshot](https://github.com/cagedb1rd/EventCraft/tree/v1.1.0).

[MIT License](LICENSE) · [Third-party notices](THIRD_PARTY_NOTICES.md) · [Verification](docs/verification-visual-v3.md)
