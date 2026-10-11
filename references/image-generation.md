# Host image generation bridge

Python cannot call an Agent's image tool directly. EventCraft separates a portable CLI artifact contract from the host's real tool invocation, avoiding an API key requirement.

```sh
eventcraft art-plan event.json --style tech-gradient --output output/art-plan.json
# Agent reads prompt, invokes built-in image_gen, inspects the returned image.
eventcraft art-import output/art-plan.json --image /real/tool/output.png --output output/art-v1
eventcraft all event.json --style tech-gradient --visual-receipt output/art-v1/receipt.json --require-art --output output/campaign
```

Use real host-returned paths; the placeholder is documentation, not a generator. Built-in outputs normally live under the host's Codex generated-images directory. Copy them into the project. Do not assume the tool accepts a destination argument. Unavailable tools mean no fresh generation: explain the limitation before offering bundled art or an explicitly authorized paid fallback.

Version 3 plans include the **actual event title**, subtitle, category/subtype, keywords, highlights, audience and design direction as semantic context. The style describes the artistic medium rather than a fixed sculpture/person/scene. `composition.py` reserves normalized title/fact/CTA coordinates before generation, expands space for long titles, and passes the same coordinates to the renderer. `typography.json` defines Chinese/English display candidates, subtitle/information/numeral stacks, weight, shape, spacing, leading, alignment and mixed-script breaking rules. Actual platform fonts are measured and recorded, never copied into the public package.

The host Agent discovers tool availability first, invokes the real tool, views returned imagery, then imports it. No third-party `image/` reference is needed at runtime. A missing tool must be reported; fallback is reusable original art and is explicitly labeled in the manifest as `reusable-art-fallback`. Python has no access to a chat's tool namespace; the installed Agent Skill performs that orchestration, not a fake local SDK call.

Inspect every final ratio. If portrait cropping destroys negative space, run `art-plan --ratio square` or `--ratio print`, actually regenerate that composition and import to a separate versioned directory. Set `assets.visual_variants.square` / `.print` to those receipt paths; export persists all variant assets/receipts relatively. Without a ratio variant, fit the complete original instead of cropping its reserved zones. Never silently stretch human subjects or cover busy imagery with opaque panels.

`manifest.checks.layouts.*.image_readability` samples the real background under the measured text-line ranges with lettering hidden. This is advisory evidence: it cannot recognize every glyph collision or certify aesthetic quality. Review flagged outputs, move the text within a new composition or regenerate, rerender, and record the visible defect/fix. All dates, venue, QR and factual lettering remain deterministic.

Import verifies raster bytes/type/pixels and writes a non-destructive receipt with prompt, style, dimensions, SHA-256 and semantic event digest. `generator=codex-imagegen` is the Agent's attestation, not cryptographic call evidence; the actual conversation tool call is the evidence. Wrong style, altered bytes or changed facts are rejected. Receipt pointer, selection style, invitation form and source bookkeeping do not change the semantic art digest.

Runtime originals in `eventcraft/data/art/` are included in wheels and complete Skill ZIPs. Each of the ten artworks was actually generated with Codex image_gen; creative briefs/hashes are in `assets/generated-art.json`. Previews can reuse them. Bundled-art and event-specific receipts remain distinct in manifests. Do not claim reuse is a new call.

Campaign exports contain an art image and relative receipt, allowing copied campaigns to rerender. No third-party reference is exported. The fictional Web Summit demonstrates the real plan/import/render path with an additional generated artwork.

The legacy optional OpenAI adapter remains explicitly opt-in for compatibility. The default Skill workflow and this visual acceptance run do not call it.
