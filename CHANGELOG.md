# Changelog

## 1.1.1 - 2026-10-14

- Remove old rendered galleries, duplicate inline-image HTML, campaign source artwork and historical QA exports from the current source tree. Preserve representative current posters, four invitations and print samples; full historical evidence remains in the v1.1.0 snapshot.
- Reorganize Chinese and English READMEs around visual examples, complete Skill installation, one-time runtime setup, event input, style choice and output viewing.
- Exclude tests, CI, development scripts and development reports from the default Skill ZIP. Keep automated test source in Git for CI and direct generated examples to ignored output directories.
- Check repeated exports for identical HTML, facts, artwork and layout, while allowing only sparse low-amplitude text antialiasing differences observed in Chromium CI. Reject background, geometry and stronger pixel changes.

## 1.1.0 - release preparation, 2026-10-12

This version is prepared in source; this changelog does not assert that a tag or Release has been published.

- Generate event-specific artistic concepts with the host Agent's actual built-in ImageGen tool, without a default API key requirement. Record honest reusable-art fallback when unavailable.
- Plan normalized composition zones before generation from event meaning, title length and output ratio; support imported square/print variants and portable receipts.
- Define ten Chinese/English typography systems, natural negative space and transparent poster text; remove default opaque title/date/footer panels.
- Simplify posters to core facts; naturally format dates, hide internal timezones by default, and make QR generation depend on scan intent or explicit policy.
- Preserve extraction, fact confirmation, three-choice/next/auto/reference selection, complete copy and batch export.
- Export four independent visual invitation structures with native PNG/PDF and two-page folded print output.
- Fix Shanghai keyword matching, CJK line/spacing measurements, composed QR sizing and reading-zone contrast.
- Fix CI module discovery, adapt title leading to measured fallback font metrics, normalize compatibility characters extracted from PDFs, and use software rendering for repeatable image exports.
- Include real 15-call visual acceptance, same-style different-event comparisons, title stress outputs and an isolated installed-Skill Word workflow.
- Default to a compact runtime Skill ZIP; full development examples are opt-in. Inspect pending as well as tracked files in release checks.

See [release notes](docs/release-notes-1.1.0.md) and [actual verification](docs/verification-visual-v3.md). Cross-platform and professional print limitations remain documented.

## 1.0.0 - 2026-10-12

- Initial ten-style campaign workflow, deterministic ranking, actual three-way previews and saved choices.
- Typed event/evidence contract, conservative document extraction and fact-based multilingual copy.
- Transactional export, asset preservation, optional provider adapters, public fictional examples and CI configuration.

The intermediate visual-system-2 work is superseded by 1.1.0; its historical evidence remains in the repository.
