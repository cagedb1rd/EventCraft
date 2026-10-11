---
name: eventcraft
description: Create a complete, fact-consistent event promotion campaign with posters, invitations, PDFs and Chinese or English copy. Use for event materials, explainable three-style recommendations, or adapting a supplied visual reference.
---

# EventCraft

Use this repository's executable CLI; install with `python -m pip install -e .` and `python -m playwright install chromium` if needed. Run commands from the skill directory or use its absolute path. Read [the event contract](references/event-schema.md) when normalizing facts, and [the workflow](references/workflow.md) for command options.

1. Understand text or attached files with available Agent capabilities, or run `eventcraft extract <input>`. Save explicit facts to `event.json` with sources, confidence and unknowns. The offline extractor is best effort, not semantic understanding. Never invent dates, venue, organizer, audience, fees or registration. Reference images change design only.
2. Run facts validation. Gather essential missing fields, date ambiguity and conflicting facts into one concise question; omit optional fields. Confirm an IANA timezone. If unresolved, stop before final generation or use explicitly labeled `--draft`. Mark confirmed fields and evidence.
3. Unless a style was explicitly chosen or automatic selection requested, run `eventcraft recommend event.json --output <state-dir>`. Show only the current three explanations, tradeoffs and **actual PNG previews**. Ask for 1/2/3, automatic choice, another batch, or a reference image. Preserve state; a number refers to the current saved list. `--next` shows the next disjoint batch; show all ten only on request. Read [recommendation behavior](docs/style-recommendation.md) for constraints.
4. Honor the user's chosen style even outside the first three. For a reference, use `--style-reference` and, without a visual provider, explain that only colors are analyzed; obtain a textual layout preference when relevant. Choose an existing original layout from the description and pass its ID explicitly. For a particular style, read only its [design guide](references/style-guides/).
5. Execute **one** `eventcraft all event.json --select 2 --state <state-dir> --output <campaign-dir>` (or `--style <id>`, `--auto-style`, `--style-reference <file>`). This produces the whole package. Do not ask separately about each asset. Use an authorized host image tool only for abstract art, then set `assets.hero_image`; factual text and QR belong to the renderer.
6. Inspect generated previews and `manifest.json`. Report actual output paths and checks. Correct visible defects and rerender the batch. Drafts and demos are never publishable. Registration URLs are checked syntactically, not fetched. Provider requests require explicit network authorization and credentials; template mode is fully local.

For high-quality Agent-written promotional prose, start from the generated fact-only copy, edit wording with the same event facts, and recheck key fields. Keep semantic facts in `event.json`; user photos, logos and QR images must retain their original content. Do not commit private references or output. Full Gallery: `eventcraft gallery`.
