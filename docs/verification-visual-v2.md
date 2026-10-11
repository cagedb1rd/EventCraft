# Local visual rebuild verification — 2026-10-12

This acceptance covers the Windows checkout only. No GitHub upload, push, repository/PR creation, release or remote CI execution occurred during this task. Earlier remote history in the previous handoff is outside this task.

## Actual generation and review

- Fourteen assigned research images were decoded and inspected for composition, subject, type, color and material. Filename/extension differences are documented in [reference study](reference-study.md). Original-file SHA-256 values were rechecked unchanged. `/image/` is ignored and has no tracked files; research sheets remain in ignored `tmp/`.
- Eleven real built-in `image_gen` calls produced ten independent original library artworks and one additional fictional Web Summit key visual. [Library provenance](../assets/generated-art.json) stores actual host-call prompts and hashes. [Web Summit receipt](../assets/campaigns/web-summit/receipt.json) binds the real returned image to event/style/hash. No OpenAI API key or paid API was used.
- Actual portrait posters and four invitation forms were visually inspected. Square outputs and Poppler rasterizations of print files were separately inspected. Visual review supplements the automated bounds/overlap checks.
- The approved new [Web Summit input](../examples/inputs/web-summit.json) is explicitly fictional. Its date, venue, organizer and `example.org` URL are demo facts, not information about a real Web Summit. Its imagined skyline is artwork, not venue evidence.

## Deliverables and evidence

| Item | Result |
|---|---|
| Complete public campaigns | 20: five existing examples, ten styles, four invitation forms, one Web Summit |
| Posters | 1080×1920 portrait, 1080×1080 square and one-page A4 PDF |
| Invitations | 1600×800 boarding pass, 1600×700 ticket, 1080×1350 formal card, 1800×1000 folded spread |
| Folded print | Separate exterior/interior PNG/HTML and two-page exterior-then-interior PDF |
| Poster facts | Title, one slogan, date/time, venue, one CTA/QR, optional organizer/logo |
| Reading surfaces | Independent opaque title, fact and CTA regions; DOM bounds/colors recorded |
| Complete Gallery | [Offline gallery](../examples/gallery/index.html), [PNG/PDF index](style-gallery.md) |
| File/PDF/layout audit | [artifact-audit.json](artifact-audit.json) |
| Composed QR / Poppler / research integrity audit | [visual-audit.json](visual-audit.json) |
| Last completed extended suite | 105 passed, one new test setup failure; [original JUnit](test-results-visual-v2.xml) |
| Corrected numbered-choice regression | [Targeted JUnit](test-results-visual-v2-targeted.xml), one passed |
| Featured campaign | [Web Summit preview](../examples/visual-v2/web-summit/preview.html) |

Actual QA discovered a formal-card QR at 110px could not be decoded from the full image with the longer demo URL. It was enlarged to 150px, given a white quiet margin and moved clear of the design serial; affected examples were rerendered. Earlier fixes addressed inline-image baseline overflow, perforations extending outside the sheet, lower-title square overflow and CJK line clipping.

Final audit: 20 complete packages, 84 PNG files (including QR/art auxiliaries), 72 PDFs and 86 validated layouts. All 72 PDFs were rendered through Poppler; 57 composed-image QRs decoded to the expected demo URLs. Fourteen original references remained byte-identical. Lint, Skill validation and local-link checks passed.

An earlier 105-test suite passed before adding the numbered-choice regression. The extended suite then returned 105 passed/one failure: its fixture saved state before rereading the serialized input, so JSON evidence defaults changed the state digest. The fixture now matches the real two-turn CLI workflow; the single corrected regression passed in 4.57 seconds. A subsequent full rerun was interrupted at the user's explicit request to stop large tests and finish the handoff. The current tree therefore has **no final complete 106-test acceptance**. Original failed results are retained rather than replaced with a claimed success.

The Windows replacement path now retries brief file-sharing failures for up to 1.8 seconds; the affected existing examples were successfully regenerated. Full tests after this small change remain deferred. Wheel/Skill archive rebuild and isolated installation smoke checks are also deferred; existing ignored `dist/` artifacts predate these changes and must not be treated as current.

## Reproduction

```sh
python -m ruff check eventcraft scripts tests
python scripts/validate_skill.py
python -m pytest -q --basetemp=tmp/pytest-visual-v2-06 --junitxml=docs/test-results-visual-v2.xml
python scripts/verify_outputs.py
python scripts/audit_visual_outputs.py
python scripts/release_check.py
python scripts/package_skill.py
python -m build --no-isolation
python scripts/isolated_smoke.py
```

Visual audit requires development OpenCV and Poppler on PATH. Its original-image hash check also requires the local supplied `/image/` and original ignored research inventory; these research files are intentionally absent from installation packages. Gallery rerendering reuses verified original art. Fresh bespoke art requires a real Agent host-tool call using [the bridge workflow](../references/image-generation.md).

## Limits

- Windows/Python 3.12/Chrome was exercised. macOS/Linux, other Agent hosts, real Tesseract OCR and legacy paid providers were not newly validated. No remote CI state was checked or changed.
- Receipts are Agent attestations plus deterministic event/hash checks, not independent proof of a host tool call. Tool availability/limits belong to the installed Codex environment; absence is reported explicitly.
- PDFs are RGB with vector text and embedded raster artwork, without CMYK conversion, bleed, crop marks or print-shop calibration. Folded PDFs are full spreads; printer duplex orientation needs checking before production printing.
- Demo QR destinations were decoded from actual images, not fetched or certified as live registration services. Supplied QR images are preserved rather than independently certified.
- Source art is approximately 1024×1536; enlarging it cannot invent source detail. Typography/QR are separately rendered at native output resolution.
- Bundled original art is reusable. Event-specific subjects require fresh generation; manifests distinguish reusable from event-bound art.
