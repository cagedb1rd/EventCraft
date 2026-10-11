"""Private reference analysis: palette-only offline, structured vision when enabled."""

import hashlib
from pathlib import Path

from PIL import Image, ImageOps
from pydantic import BaseModel, Field, field_validator

from ..schema import Brand, Event
from ..security import image_uri, local_file
from . import OpenAIProvider


class StyleOverride(BaseModel):
    base_style: str
    mode: str = "palette-only"
    colors: list[str] = Field(default_factory=list, max_length=5)
    typography: str = ""
    grid: str = ""
    density: str = ""
    decoration: str = ""
    atmosphere: str = ""
    limitations: list[str] = Field(default_factory=list)
    reference_hashes: list[str] = Field(default_factory=list)
    description: str = ""

    @field_validator("colors")
    @classmethod
    def colors_valid(cls, value: list[str]) -> list[str]:
        return Brand(colors=value).colors


def analyze_references(
    event: Event, paths: list[str], base_style: str, *, root: Path | None = None,
    provider: OpenAIProvider | None = None, description: str = "",
) -> StyleOverride:
    from ..recommendation import profiles

    if not 1 <= len(paths) <= 5:
        raise ValueError("Provide between one and five reference images")
    palette = []
    hashes = []
    uris = []
    for value in paths:
        path = local_file(value, root)
        uri = image_uri(path, root)
        uris.append(uri)
        hashes.append(hashlib.sha256(path.read_bytes()).hexdigest())
        with Image.open(path) as image:
            image = ImageOps.exif_transpose(image).convert("RGBA")
            background = Image.new("RGBA", image.size, "white")
            background.alpha_composite(image)
            thumb = background.convert("RGB")
            thumb.thumbnail((128, 128))
            quant = thumb.quantize(colors=5)
            values = quant.getpalette()
            for _, index in sorted(quant.getcolors(), reverse=True):
                rgb = values[index * 3:index * 3 + 3]
                color = "#" + "".join(f"{c:02x}" for c in rgb)
                if color not in palette:
                    palette.append(color)
    result = StyleOverride(
        base_style=base_style, colors=palette[:5], reference_hashes=hashes, description=description,
        limitations=["仅分析颜色；未理解文字、网格或原图构图。请用 --style-description 补充版式偏好。"],
    )
    if description and not event.style:
        for sid, profile in profiles().items():
            if any(term.lower() in description.lower() for term in [sid, profile["name"], profile["name_en"]]):
                result.base_style = sid
                break
    if provider:
        instruction = (
            "Analyze abstract design characteristics, not event facts or private text. "
            "Return colors, typography, grid, density, decoration, atmosphere and select base_style from "
            + ", ".join(profiles()) + ". Do not copy protected illustrations, logos or exact compositions. "
            + "User preference: " + description
        )
        analyzed = provider.structured(
            [{"type": "input_text", "text": instruction}]
            + [{"type": "input_image", "image_url": uri} for uri in uris],
            StyleOverride.model_json_schema(), "style_override",
        )
        result = StyleOverride.model_validate(analyzed)
        result.mode = "vision"
        result.reference_hashes = hashes
        result.description = description
    # A user-specified layout always wins. Reference input wins over recommendations.
    if event.style:
        result.base_style = event.style
    if result.base_style not in profiles():
        raise ValueError("Reference analysis returned an unknown base layout")
    forbidden = event.brand.forbidden_colors
    result.colors = [c for c in result.colors if c not in forbidden]
    if event.brand.colors:
        result.colors = event.brand.colors[:5]
    return result
