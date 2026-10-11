# EventCraft

**Event facts → three real style previews → one choice → one complete campaign.**

![Actual generated examples](docs/images/selection-workflow.png)

[中文](README.md) · [Ten-style Gallery](docs/style-gallery.md) · [Verification](docs/verification.md)

EventCraft is an executable Agent Skill and standalone Python CLI. It produces portrait and square posters, a digital invitation, two A4 PDFs, four copy variants, canonical facts, manifest and an offline preview. Ten authored layout systems provide actual visual distinctions. All included examples are fictional and generated locally using Chromium, without API keys.

Display fonts and weights vary by style. Actual title width determines balanced wrapping and an expanded full-width structure for longer headings. See the [real short/medium/long comparison](docs/images/title-adaptation.png); reproduce it with `python scripts/build_title_showcase.py`.

## Install and run

Python 3.11+, Chromium and a CJK font are required. Windows uses Microsoft YaHei/SimSun; macOS PingFang/Songti; Linux should install Noto CJK.

```sh
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m playwright install chromium
eventcraft all examples/inputs/lecture.json --auto-style --output output/lecture
```

Open `output/lecture/preview.html`. Offline template rendering never fetches remote assets. Windows may reuse installed Chrome/Edge. `EVENTCRAFT_BROWSER` supplies an explicit executable path.

```sh
eventcraft recommend examples/inputs/lecture.json --output output/selection
eventcraft all examples/inputs/lecture.json --select 2 --state output/selection --output output/chosen
eventcraft recommend examples/inputs/lecture.json --output output/selection --next
eventcraft render examples/inputs/lecture.json --style retro-print --output output/retro
eventcraft all examples/inputs/lecture.md --interactive --output output/interactive
eventcraft extract examples/inputs/lecture.md --output output/extracted/event.json
eventcraft gallery --output output/gallery
```

The default workflow presents only three options. Ranking, reasons, current page and numbered choices persist; changes invalidate stale choices. Explicit styles and references take priority; hard brand constraints remain enforced. Ranking is an explainable engineering heuristic, not objective aesthetic measurement. [Algorithm](docs/style-recommendation.md)

Inputs: JSON, labeled UTF-8 text/Markdown, DOCX, text-layer PDF and optional Tesseract screenshots. Offline extraction is conservative and does not understand arbitrary implicit meanings. Essential missing facts stop finished generation; `--draft` marks unresolved work visibly. Optional organizer, fee, speaker and recipient are never invented. Chinese and English labels/copy are supported; mixed supplied text is accepted. Facts are not automatically translated.

![Real ten-style overview](docs/images/style-contact-sheet.png)

Styles: `swiss-grid`, `editorial-minimal`, `tech-gradient`, `academic-clean`, `neo-brutal`, `retro-print`, `neon-night`, `warm-playful`, `luxury-elegant`, `sports-dynamic`. [Paired poster/invitation gallery](docs/style-gallery.md)

```sh
eventcraft render examples/inputs/dinner.json --style luxury-elegant --style-reference examples/inputs/palette.png --output output/custom
python scripts/generate_examples.py
python scripts/generate_style_gallery.py
ruff check eventcraft scripts tests
python scripts/validate_skill.py
pytest -q
python -m build
```

Reference mode extracts only verifiable palette data offline. Supply a layout ID or description naming a built-in style. It persists reproducible overrides and does not embed private references. Logos, hero photos and QR assets use contain. QR codes are generated only from actual syntactically valid URLs; tests decode both source codes and composed posters.

Optional OpenAI extraction/vision/image generation requires `OPENAI_API_KEY` and explicit `--allow-network`, with potential API fees. No live paid provider calls were run during this delivery. External contracts and failure handling are tested offline. [Provider setup and limitations](docs/providers.md)

Output: 1080×1920 `poster_portrait.png`, 1080×1080 `poster_square.png`, 1080×1350 `invitation.png`, `poster_print.pdf`, `invite_letter.pdf`, four files in `copy/`, `event.json`, `manifest.json`, `preview.html`, editable HTML sources and optional QR/override files. Print PDFs are A4 RGB, not CMYK/bleed production files. Actual DOM bounds, font usage, facts, dimensions, pages and contrast are recorded.

Install the repository as the `eventcraft` skill and its CLI, then invoke `$eventcraft`; [Agent usage](docs/skill-usage.md). Private outputs and `.env` are ignored. `--input-root` restricts input paths; local assets have size limits. URLs are syntax checked, never automatically fetched. System fonts and third-party art are not bundled.

MIT licensed. [Third-party notices](THIRD_PARTY_NOTICES.md) · [Architecture](docs/architecture.md) · [Contribution guide](CONTRIBUTING.md) · [Release instructions](docs/release.md). No GitHub repository was created or uploaded during this work. GitHub Actions is prepared but its remote execution awaits publication.
