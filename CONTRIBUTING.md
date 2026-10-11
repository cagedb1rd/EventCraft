# Contributing

Use Python 3.11+, an isolated environment, Chromium and system CJK fonts. Install `.[dev]`, then run `ruff check eventcraft scripts tests`, `python scripts/validate_skill.py`, `python scripts/release_check.py`, `pytest -q` and `python -m build`.

## Design sources

Preserve the ten public style IDs. Artistic media/composition language live in `eventcraft/data/visual-systems.json`; native typography contracts live in `eventcraft/data/typography.json`; ranking profiles live in `eventcraft/data/style-profiles.json`. Keep the public `assets/styles` mirrors and `references/style-guides` consistent. `scripts/build_design_assets.py` synchronizes the current canonical catalog and guides; it must not restore old fixed-subject or opaque-panel definitions.

New visual work needs an event-specific semantic brief, composition planning before actual generation, final-image inspection and correction when needed. A prompt or receipt alone is not proof of a real tool call. Use the public renderer and preserve accurate facts. Transparent natural reading areas, native Chinese typography and distinct invitation structures are required; color-only variants are insufficient.

Ranking edits retain determinism, fact-grounded reasons, brand exclusions and saved selection state. Add behavioral regressions for actual bugs. Extraction must retain evidence and uncertainty; never infer event facts from preference cues.

## Public files and evidence

Keep private inputs, references, keys and generated user campaigns out of Git. Only explicitly fictional public examples belong in `examples/`. Do not alter the user's local `/image/` research files or bundle commercial fonts. Provider mocks must be described as mocks. Archive packaging defaults to the runtime Skill; `--with-examples` is for complete development material.

Inspect contact sheets and PDF pages after visual changes. Record the actual environment, tool calls, test snapshots and unverified limits; do not merge separate test runs into a fictional new full-suite result. Current visual evidence is [v3 verification](docs/verification-visual-v3.md); older reports remain historical. The maintainer controls commits, pushes and releases; no automatic publishing step exists.
