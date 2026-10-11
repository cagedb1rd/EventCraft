# Executable workflow

The current Agent workflow is [SKILL.md](../SKILL.md): after selection, actually call built-in image_gen through [the host asset bridge](image-generation.md). CLI preview reuse needs no API key. Final poster text uses natural low-complexity image regions and only title/short supplied subtitle/time/location/optional CTA/QR/organizer. No universal opaque rescue panels. Timezones are hidden and QR requires explicit scan intent. Invitations/copy retain detail.

```sh
eventcraft art-plan event.json --style tech-gradient --output output/art-plan.json
# Real host image_gen invocation by the Agent, followed by inspection.
eventcraft art-import output/art-plan.json --image /real/generated/image.png --output output/art-v1
eventcraft all event.json --select 2 --state output/selection --visual-receipt output/art-v1/receipt.json --require-art --output output/selected
eventcraft all event.json --style luxury-elegant --invitation-format formal-card --output output/card
```

`--invitation-format` accepts `auto`, `boarding-pass`, `ticket-stub`, `formal-card`, `folded`. Visual invitation PNG/PDF are primary outputs; the text letter is additional. Folded output includes inside/outside PNGs and a two-page print file. Fresh artwork is facts/style/hash bound. Exported art/receipt paths are relative for relocatable replay. Do not alter event facts between numbered recommendation and selection without regenerating state.

```sh
eventcraft extract examples/inputs/lecture.md --output output/extracted/event.json
eventcraft recommend examples/inputs/lecture.json --output output/selection
eventcraft recommend examples/inputs/lecture.json --output output/selection --next
eventcraft all examples/inputs/lecture.json --select 2 --state output/selection --output output/selected
eventcraft all examples/inputs/lecture.json --auto-style --output output/automatic
eventcraft render examples/inputs/dinner.json --style luxury-elegant --output output/dinner
eventcraft render examples/inputs/sports.json --style sports-dynamic --output output/sports
eventcraft gallery --output output/gallery
```

`--page 2` equals next batch. `--all` is opt-in full catalog. Scores, component contributions, input/config digests, preview checks and selection source are serialized. Default state directory: `output/.state/<slug>`. `--state` overrides this for resumed selection. Event changes invalidate numbered choices. An explicit style has priority over `--select` and `--auto-style`. A reference overrides recommendation interaction; explicit style controls its base layout. Hard brand constraints still apply.

`eventcraft all input.docx --interactive` makes one combined fact question, accepting a JSON patch, then displays actual preview paths for choice. It supports another batch, full Gallery and `reference:<path>`. If facts remain unresolved after the combined patch, it stops. `uncertainties: []` is an explicit user declaration that those ambiguities were resolved. CLI is designed for a terminal; an Agent should ask naturally and maintain event/state files.

Exit codes: 0 succeeded, 2 invalid input/facts/layout/provider, 3 previews produced awaiting style choice, 130 interaction cancelled. `extract` returns 0 when best-effort conversion succeeds even if questions remain. Always read `questions.json`. `all` never silently finishes incomplete facts; `--draft` watermarks assets and declares publishable false.

Local generation does not need an API key or connectivity. Input images are data URIs, all CSS is inline, all output preview links are relative. Preserve user references outside the public repository. Bundle source HTML is supplied for later edits. The renderer verifies all outputs in staging before replacing generated files in an existing campaign. It refuses unrelated nonempty output directories.
