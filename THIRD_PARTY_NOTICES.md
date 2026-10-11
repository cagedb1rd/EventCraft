# Third-party notices

EventCraft source and authored SVG/CSS are MIT. Examples are fictional. No network reference artwork, commercial template, system font or icon pack is redistributed.

Runtime dependencies retain their own licenses: Python (PSF), Pydantic (MIT), Playwright (Apache-2.0), Pillow (MIT-CMU), pypdf (BSD-3-Clause), python-docx (MIT), qrcode (BSD), tzdata (Apache-2.0 and public-domain IANA data). Development dependencies include pytest (MIT), Ruff (MIT), PyYAML (MIT), build (MIT), OpenCV (Apache-2.0), NumPy (BSD). Consult installed distributions for complete license files and notices; dependencies are downloaded independently, not vendored into the repository.

Chromium/Chrome/Edge and system CJK fonts are external runtime prerequisites with their own terms. Fonts are resolved from the operating system and used to render user artifacts, not bundled in the project or skill archive. OpenAI is an optional external service; its branding is not used as project artwork. Source research links and rights notes are in `docs/design-research.md`.
## Original generated art and local research

`eventcraft/data/art/` and `assets/campaigns/` contain original AI-generated art created with built-in Codex image_gen, not downloaded design references. `/image/` contains local third-party research references; it is excluded from Git and distributable packages. Reference imagery is not licensed or redistributed by this project. System fonts remain external to the package.
