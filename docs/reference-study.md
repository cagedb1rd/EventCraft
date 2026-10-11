# Local reference study, 2026-10-12

All fourteen supplied images were decoded and visually inspected. The table records the names assigned in the earlier development stage. This v3 upgrade preserves those names, paths and contents unchanged; no reference is embedded into a deliverable. Read-only research sheets live in ignored `tmp/reference-study/`. Third-party originals remain in ignored `/image/`, which is excluded from both packaging allowlists and Git.

| Assigned design | Actual matched file | Observed composition, visual, type and material | Original implementation |
|---|---|---|---|
| Swiss Grid | `swiss-grid.jpg` | Vermilion field, radical oversized diagonal type, black/white contrast, asymmetric information | Original silkscreen circles/strips; strong asymmetric headline, independent facts bar |
| Editorial Minimal | `editorial-minimal.jpg` | Oblique black/white face crop, serif exhibition typography, black paper and open editorial spacing | Original plaster-face photography; photograph-led upper half and serif lower reading area |
| Tech Gradient | `tech-gradient.png` | Dimensional luminous head, purple/cyan mesh, dark space, powerful left type | Original glass neural sculpture; immersive hero with dark title and information layers |
| Academic Professional | `academic-professional.jpg` | City panorama, torn architecture collage, cyan lower research block, sober sans serif | Original imagined city/blueprint collage; clear pale research band |
| Neo-Brutalism | `neo-brutalism.jpg` | Acid yellow, monochrome cutouts, ink splatter, hand gesture, distressed blocks | Original cutout/foil/gesture collage; hard ink headline plate and acid information base |
| Retro Print | `retro-print.webp` | Warm distressed paper, condensed bold print, pictorial sepia lower half, letterpress character | Original halftone pianist/starburst art; slab serif, paper reading surfaces and double border |
| Neon Nightlife | `neon-nightlife.webp` | Radial mirrored tunnel, black chrome focal object, green/cyan/magenta illumination | Original intricate tunnel/beetle CG; lower display type on dark reading surface |
| Warm Illustrated | `warm-illustrated.png` | Cheerful market scene, parasols/people/patterns, turquoise/coral/ochre gouache | Original hand-painted community market; cream title space and simple warm facts base |
| Luxury Elegant | `luxury-elegant.avif` | Symmetric stepped Art Deco foil frame, sunbursts, central serif ceremony axis | Original embossed gold geometry on emerald cotton paper; central quiet reading axis |
| Sports Dynamic | `sports-dynamic.png` | Large running figures, orange/blue painted diagonals, energetic foreground crop | Original low-angle runners; petrol display/information base and diagonal action field |
| Boarding Pass | `boarding-pass.png` | Long horizontal body, detachable stub, perforation/cutouts, compact field labels | 1600×800 premium body/stub, original art band, design serial, QR and clear date/location |
| Ticket Stub | `ticket-stub.jpg` | Parchment, ticket edges, admission stub, double borders and ticket number | 1600×700 print ticket, scalloped edges, tear line, serial and separate stub |
| Formal Invitation Card | `formal-invitation.webp` | Ecru stock, thin traditional frame, quiet centered serif typography and generous space | 1080×1350 ceremonial card with double frame or matching Deco foil art |
| Folded Invitation | `folded-invitation.webp` | Photographic cover, multi-panel open spread, interior details and folding structure | 1800×1000 bifold exterior/back+cover and separate interior; two-page print PDF |

The target names preserve each image actual format and extension. Four source extensions differed from the request table: Tech Gradient is PNG, Retro Print is WEBP, Luxury Elegant is AVIF, and Folded Invitation is WEBP. The Retro Print source UUID contains `8b0e` rather than `8b0c`. No reference was missing or substituted. The unusually large academic scan (219 MP) was decoded only by the local research helper with an explicit trusted-input pixel cap; normal campaign assets retain the 24 MP limit.

All new model images are text-free originals derived from observed design language. Actual prompt sets and hashes are in `assets/generated-art.json`; runtime images are under `eventcraft/data/art/`. Event facts, QR and typography are renderer-owned. Reference art is never reused as campaign art.
