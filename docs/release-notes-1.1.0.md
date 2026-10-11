# EventCraft 1.1.0

Prepared release notes, 2026-10-12. A version in source does not mean its GitHub tag or release assets already exist.

EventCraft now plans a complete composition before generating the key visual. The host Codex Agent uses the currently available built-in ImageGen tool to create an original concept for each new event; Python then typesets exact facts into natural quiet areas. Ten styles define artistic media, Chinese/English typography and spatial relationships rather than ten fixed backgrounds.

## What changes

- Shared pre-generation composition contracts adapt to title length and portrait/square/print ratios.
- Ten native typography systems cover title, subtitle, information and numbers; actual platform fallback fonts are recorded.
- Poster text is transparent by default. Dates are human-readable; internal timezones are hidden unless requested. QR is optional and requires scan intent or an explicit policy.
- Boarding Pass, Ticket Stub, Formal Card and Folded Invitation have independent structures and real PNG/PDF exports.
- Existing extraction, confirmation, three-style recommendations, next/auto/reference choices and complete campaign exports are retained.

[Current Gallery](style-gallery.md) · [Different events in one style](../examples/visual-v3/dynamic-comparison.png) · [Title stress](../examples/visual-v3/title-gallery.png)

## Installation and upgrade

Use `eventcraft-skill-1.1.0.zip` for the complete runtime Skill, including bundled preview artwork and input samples. The default archive omits large rendered development galleries; documentation links for omitted evidence point to source. `eventcraft-skill-1.1.0-with-examples.zip` is optional and much larger. The wheel installs the CLI, not Codex instructions. Python dependencies, browser and CJK fonts must be installed separately.

Back up local modifications in an existing Skill, replace its complete directory, and reinstall the CLI in the intended environment. Confirm `eventcraft.__version__ == "1.1.0"`. Existing event/campaign receipts remain supported. A registration URL alone no longer implies QR; set `qr_policy=show` if required. Set `show_timezone=true` and a readable `timezone_label` when needed.

## Verification and limits

Actual v3 acceptance used 15 ImageGen calls, 16 complete campaign packages and 60 PDFs/66 rasterized pages. A full regression snapshot passed 111 tests; later related regressions passed 23 tests and final contracts passed 6. These are separate runs, not a claim of a fresh complete run after every change. Three composed QRs decoded correctly. Visual inspection found and corrected square/title collisions and art-medium mismatches through actual regeneration.

[Detailed evidence](verification-visual-v3.md) records the tested Windows environment, actual inspection coverage and remaining limits. Linux/macOS fonts, live OCR and paid API use are not newly certified. Pixel sampling is advisory; RGB PDFs do not include CMYK, bleed or physical duplex calibration. Remote CI must be assessed for the actual release commit.

Runtime tools never silently switch to a paid API. Third-party references in `/image/`, fonts, credentials and private inputs are excluded from packages.
