# Event contract

`eventcraft.schema.Event` is the authoritative runtime schema. Export JSON Schema with `python scripts/export_schema.py`; the checked-in machine contract is `assets/event.schema.json`.

Required for finished output: `title`, `start` (ISO datetime with year and time), `timezone` (IANA), either `venue` or `online_platform`, and either `registration` or a syntactically valid `registration_url`. “无需报名 / No registration needed” is an explicit valid registration method. End, price, organizer, speakers, contact and recipient are optional, never fabricated. Missing recipient uses a generic salutation. `end` supports crossing midnight and multiple days. UTC offsets must agree with the timezone; ambiguous DST times require an offset.

Categories are open strings; supported recommendations include lecture, workshop, recruitment, sports, esports, exhibition, market, launch, opening, birthday, community, forum, academic, wedding, dinner, awards, night-party. Unknown categories receive general ranking. Formality: unknown, casual, professional, ceremonial. Venue mode: unknown, indoor, outdoor, online, hybrid. Language: zh, en, bilingual (mixed supplied text, Chinese labels; it does not invent translations).

`sources` maps each field to `{source, excerpt, confidence: 0..1, status: provided|extracted|inferred|confirmed}`. Extracted excerpts come from the supplied input. Only low-risk category/formality can be inferred. `confirmed_fields` stores actual user confirmation; `uncertainties` blocks finished generation until resolved. Structured JSON is treated as user-provided facts, not independently verified facts.

`brand` supports `colors`, `forbidden_colors` (#RRGGBB), `forbidden_styles`, `high_contrast`, `preserve_logo`. Foreground contrast is always ≥4.5, also when high_contrast is false. Required and forbidden colors cannot overlap. Presets violating forbidden colors are excluded, unless the required palette replaces them. An explicitly forbidden style cannot be selected.

`assets`: logo, hero_image, speaker_photo, qr_image and style_reference (list of 1–5 paths). Only PNG/JPEG/WebP. The first four appear in outputs with contain; reference images are analyzed but never embedded. Use `--input-root` to restrict every source and asset. Relative asset paths are resolved relative to the process directory: run from the project root or use absolute paths. File limit 20 MiB, image limit 24 MP; PDF ≤100 pages; DOCX expanded ≤80 MiB.

`demo: true` labels fictional examples. Example domains have no real event-registration purpose. `style`, `style_description`, `atmosphere`, `keywords`, `audience`, `channels`, `highlights`, `speakers`, `teams` affect presentation or ranking. A reference analysis stores only abstract features and hashes in `style_override.json`, without OCR text or private file names.
