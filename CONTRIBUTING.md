# Contributing

Use Python 3.11+ and an isolated environment. Install `.[dev]`, Chromium and CJK fonts. Run `ruff check eventcraft scripts tests`, `python scripts/validate_skill.py`, `pytest -q` and `python -m build`.

New designs need independent structure, tokens/profile/guide consistency, genuine previews and all three-format bounds tests. Preserve the ten existing public IDs. Catalog/guide edits originate in `scripts/build_design_assets.py`, then regenerate both asset and package copies. Do not replace layouts with color-only variants.

Ranking edits must retain determinism, fact-grounded reasons, hard exclusions, cross-turn state and versioned config. Add behavioral regression cases when resolving actual bugs. New extractors need evidence and conservative uncertainty; never infer sensitive/event facts from preference cues.

Keep private inputs, references, keys and generated user campaigns out of Git. Only clearly fictional public examples go in `examples/`. Link research sources without bundling unlicensed photos/fonts/templates. All contributed code and original artwork is MIT. Provider contract mocks must be described as mocks, never live verification.

Reproduce public assets with the scripts; inspect contact sheets and PDF pages after layout changes. Document observable verification and actual limitations in `docs/verification.md`. A maintainer chooses repository visibility and publishes; no automated publish step exists.
