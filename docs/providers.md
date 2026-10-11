# Optional provider boundaries

The preferred Agent path now uses built-in Codex `image_gen`, followed by `art-import` and deterministic typesetting. It does not require `OPENAI_API_KEY`. See [the complete host workflow](../references/image-generation.md). Bundled previews are original generated artwork; the current v3 acceptance separately records 15 real calls for event-specific art and corrective compositions. See [current evidence](verification-visual-v3.md). The CLI itself cannot invoke a host tool; plans alone are not generated images. The descriptions of original SVG template mode below are historical, and the API adapter remains an explicitly authorized compatibility path.

Template mode, ranking, fact-only copy, color extraction, original SVG, QR generation, screenshots and PDFs require no external account or API key. Installation downloads are separate from runtime.

The implemented optional adapter uses official `POST https://api.openai.com/v1/responses` and `POST https://api.openai.com/v1/images/generations`. It accepts an environment variable `OPENAI_API_KEY`, never an inline CLI key, and requires explicit `--allow-network`. Responses model defaults to `gpt-4.1-mini`, overridable with `--model`. Abstract image generation uses `gpt-image-1`, with no factual text/logo/QR in its prompt; the returned image becomes a user-visible hero asset.

`extract --llm` sends text and a JSON Schema, parses structured results, validates the Event schema, then requires factual review. This does not prove semantic correctness or source fidelity. `--vision` sends up to five bounded data URIs and asks for abstract color, typography, grid, density, decoration, atmosphere and a base preset. No private OCR text or reference image is copied to the public output. The renderer implements the selected original base layout and palette rather than cloning detailed original compositions; additional characteristics are persisted as analysis metadata.

Without vision, reference analysis quantizes downsampled pixels and reports `palette-only`. It cannot understand hierarchy/grid/fonts. A textual preference naming a preset selects that base layout; an explicit style always wins. Save `style_override.json` and replay it with `--style-override` to avoid sending/analyzing original references again.

```sh
eventcraft render examples/inputs/dinner.json --style luxury-elegant --style-reference examples/inputs/palette.png --output output/custom
eventcraft render examples/inputs/dinner.json --style-override output/custom/style_override.json --output output/custom-replay
```

Provider timeout is 90 seconds, maximum returned bytes 32 MiB. HTTP failures omit bodies to protect private prompts. No automatic retry or background request. API fees/model permission may apply. Current deliverable tested offline request payloads, structured parsing, precedence, color constraints, key/opt-in gating and failure branches; no real paid request was made. Native host image generation can also be used by an authorized Agent, importing the resulting image with `art-import` and passing its receipt to `--visual-receipt --require-art`.

OCR: install `python -m pip install -e '.[ocr]'`, then separately install Tesseract and `chi_sim` + `eng` language data. `eventcraft extract image.png --ocr` reports errors if unavailable. The delivered environment does not have Tesseract; its real image OCR execution is unverified. Text-layer PDF/DOCX extraction is independent of OCR.
