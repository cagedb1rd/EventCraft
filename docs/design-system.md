# EventCraft visual system 3

The existing fact extraction, confirmation, three-choice recommendation, batch copy and export pipeline is retained. Ten styles are public artistic and typographic instructions, not ten fixed backgrounds. The formal installed Agent workflow discovers the available built-in image tool, constructs event-specific imagery, inspects it and imports a real artifact before rendering.

`visuals.py` passes title, subtype, keywords, audience and theme to ImageGen. `composition.py` decides natural quiet zones from title length and ratio **before** generation; those same coordinates control poster text. `typography.json` supplies ten distinct Chinese/English display stacks, weights, shapes, tracking, leading, role scales and breaking rules. Browser measurements include tracking and native glyph bounds; actual platform fonts are recorded. No font files are redistributed.

Posters render transparent text regions directly on planned natural negative space. Swiss silkscreen geometry, letterpress frames and Brutalist accents are authored visual language; there is no universal title plate/date ribbon/footer card. A real pixel sampling pass can move headline alignment within the planned quiet region. Unresolved samples require human/Agent visual inspection and re-composition, not automated aesthetic certification.

Portrait, square and A4 exports retain native output sizes. A ratio-specific image can be generated from `art-plan --ratio square/print`, imported and referenced in `assets.visual_variants`. All artwork/receipts export relatively and survive relocation. Without a ratio variant, the full portrait artwork is preserved rather than destructively center-cropped. This safe fallback can leave visible framing; generate the alternate ratio for polished full-bleed results.

A poster contains title, at most one short supplied subtitle, natural date/time, venue and only useful CTA/brand/QR. Full introduction, highlights, fee and registration details remain in invitations/copy. Internal timezones and ISO datetimes are hidden by default. Explicit timezone requests use a readable label. A URL alone does not create QR; explicit scan intent or qr_policy=show does. No-link scan requests are actionable missing data; absent QR leaves no placeholder.

Four invitation forms are independent compositions: Boarding Pass body/stub/perforation, Ticket Stub tear-off/serial, Formal Card ceremonial frame/paper/type, Folded cover/back/interior/two-page spread PDF. Information may be richer than a poster. Dates are not repeated in a header. QR stays optional with a valid quiet zone.

Current real artifacts and acceptance evidence are in [v3 acceptance](verification-visual-v3.md) and [Gallery](style-gallery.md). Earlier v2 evidence remains historical and does not describe the present renderer.
