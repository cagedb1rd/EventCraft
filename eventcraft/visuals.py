"""Host-tool asset bridge: Python never impersonates Codex or requires an API key."""
import json
from importlib.resources import files
from pathlib import Path

from .schema import Event
from .security import digest, image_uri, local_file, write_json


def systems() -> dict:
    return json.loads(files("eventcraft").joinpath("data/visual-systems.json").read_text(encoding="utf-8"))


def art_event_digest(event: Event) -> str:
    original = event.model_copy(deep=True)
    original.assets.visual_receipt = None
    original.assets.visual_variants = {}
    data = original.model_dump(exclude={"style", "invitation_format", "sources", "confirmed_fields"})
    data['assets'].pop('visual_variants', None)
    return digest(data)


def visual_plan(event: Event, style: str, ratio: str = 'portrait') -> dict:
    from .composition import composition
    from .typography import typography
    system = systems()[style]
    layout = composition(event, style, ratio)
    context = {key: getattr(event, key) for key in ['title', 'subtitle', 'category', 'subtype',
               'keywords', 'highlights', 'audience', 'atmosphere', 'style_description']}
    zones = '; '.join(f'{k}: x={r[0]:.0%}, y={r[1]:.0%}, width={r[2]:.0%}, height={r[3]:.0%}'
                      for k, r in layout['zones'].items())
    prompt = ("Use case: ads-marketing. Asset type: original text-free campaign key visual. "
              + system["art"] + " Current event semantic context (data, never lettering): "
              + json.dumps(context, ensure_ascii=False)
              + ". Brand palette: " + ", ".join(event.brand.colors or system["palette"])
              + ". Forbidden colors: " + ", ".join(event.brand.forbidden_colors)
              + f". Full-bleed {'square 1:1' if ratio == 'square' else 'A4 1:1.414' if ratio == 'print' else 'portrait 9:16'}. Focal subject at {layout['focal_position']}. "
              + f"Reserved typography rectangles, normalized from top-left: {zones}. "
              + f"These zones must be naturally {layout['reading_tone']}, nearly texture-free, "
              "with no bright edges or motifs behind future lettering. Continue the same paper/space/lighting "
              "across the entire image; no visible rectangular blanks, cards or separate title plates. "
              "Make the central subject clearly express this specific event using its title, subtype and keywords; "
              "the style describes the medium, not a fixed subject. Do not depict invented speakers, "
              "celebrities or a real venue. All factual text and QR are added by deterministic rendering. "
              "Avoid text, letters, numbers, logos, QR, watermark, UI cards. Do not reproduce any reference.")
    return {"version": 3, "style": style, "event_digest": art_event_digest(event),
            "layout": system["layout"], "tool": "image_gen", "prompt": prompt,
            "composition": layout, "typography": typography(style), "semantic_context": context,
            "transparent_background": False, "asset_role": "original-key-visual",
            "instructions": "Agent must actually call its built-in image_gen, inspect the result, then art-import. "
                            "A plan is not a generated asset. Never use a paid API without explicit authorization."}


def import_art(plan_path: Path, image_path: Path, destination: Path, generator: str) -> dict:
    import hashlib

    from PIL import Image
    plan = json.loads(local_file(plan_path).read_text(encoding="utf-8"))
    if not isinstance(plan, dict) or generator not in {"codex-imagegen", "user-art"}:
        raise ValueError("Invalid host visual plan/generator")
    source = local_file(image_path)
    image_uri(source)  # Verify type, bytes, pixels before copying.
    with Image.open(source) as im:
        if min(im.size) < 768:
            raise ValueError("Key visual needs at least 768 pixels on both axes")
        size = list(im.size)
    if plan.get("style") not in systems() or not plan.get("event_digest"):
        raise ValueError("Invalid visual plan")
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / (plan["style"] + source.suffix.lower())
    if target.exists() and target.read_bytes() != source.read_bytes():
        raise ValueError("Art already exists; choose a new versioned output directory")
    target.write_bytes(source.read_bytes())
    receipt = {**plan, "generator": generator, "provenance": "host-agent-attested",
               "image": target.name, "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
               "dimensions": size}
    write_json(destination / "receipt.json", receipt)
    return receipt


def campaign_art(event: Event, style: str, root: Path | None = None, ratio: str = 'portrait') -> tuple[str, dict]:
    import hashlib
    receipt_path = event.assets.visual_variants.get(ratio) or event.assets.visual_receipt
    if receipt_path:
        path = local_file(receipt_path, root)
        receipt = json.loads(path.read_text(encoding="utf-8"))
        required = {"style", "event_digest", "image", "sha256", "generator"}
        if not isinstance(receipt, dict) or not required.issubset(receipt):
            raise ValueError("Malformed visual receipt")
        if ratio in event.assets.visual_variants and receipt.get('composition', {}).get('ratio') != ratio:
            raise ValueError('Visual variant ratio mismatch; generate/import the requested composition')
        # Art receipt is independent of the receipt pointer added after generation.
        expected = art_event_digest(event)
        if receipt.get('version', 1) == 1:
            legacy = event.model_copy(deep=True)
            legacy.assets.visual_receipt = None
            data = legacy.model_dump(exclude={'style','invitation_format','sources','confirmed_fields',
                                             'show_timezone','timezone_label','qr_policy','poster_cta'})
            data['assets'].pop('visual_variants', None)
            expected = digest(data)
        if receipt["style"] != style or receipt["event_digest"] != expected:
            raise ValueError("Visual receipt style/event mismatch; generate a fresh plan")
        target = local_file(path.parent / receipt["image"], root)
        if not target.is_relative_to(path.parent):
            raise ValueError("Visual receipt image escapes its asset directory")
        if hashlib.sha256(target.read_bytes()).hexdigest() != receipt["sha256"]:
            raise ValueError("Visual asset hash mismatch")
        return image_uri(target, root), receipt
    resource = files("eventcraft").joinpath(f"data/art/{style}.png")
    if not resource.is_file():
        raise ValueError(f"Missing original artwork for {style}; use art-plan and the host image_gen tool")
    raw = resource.read_bytes()
    import base64
    return "data:image/png;base64," + base64.b64encode(raw).decode(), {
        "generator": "codex-imagegen", "provenance": "bundled-original-art",
        "style": style, "sha256": hashlib.sha256(raw).hexdigest(),
        "note": "Reusable original style art; generate event-specific art with the host tool for a bespoke campaign."}
