"""Read-only local reference study sheets; never distribute the third-party images."""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
Image.MAX_IMAGE_PIXELS = 300_000_000  # Explicit trusted local research scan (219 MP).
NAMES = [
    ("Swiss Grid", "d0898"), ("Editorial Minimal", "685d7532"),
    ("Tech Gradient", "053e9412"), ("Academic Professional", "Poster_L02"),
    ("Neo-Brutalism", "371a1e"), ("Retro Print", "5_6883"),
    ("Neon Nightlife", "472261"), ("Warm Illustrated", "try_next"),
    ("Luxury Elegant", "art-deco"), ("Sports Dynamic", "8b325437"),
    ("Boarding Pass", "4145aa"), ("Ticket Stub", "cHJp"),
    ("Formal Invitation Card", "simple_elegant"), ("Folded Invitation", "il_fullxfull"),
]

def main():
    target = ROOT / "tmp/reference-study"
    target.mkdir(parents=True, exist_ok=True)
    records = []
    for start in range(0, len(NAMES), 5):
        sheet = Image.new("RGB", (1500, 1100), "#ddd9d1")
        draw = ImageDraw.Draw(sheet)
        for i, (label, prefix) in enumerate(NAMES[start:start+5]):
            matches = list((ROOT / "image").glob(prefix + "*"))
            if len(matches) != 1:
                raise ValueError(f"Ambiguous/missing reference {prefix}: {matches}")
            path = matches[0]
            with Image.open(path) as im:
                records.append({"style": label, "file": path.name, "size": list(im.size),
                                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
                thumb = ImageOps.contain(im.convert("RGB"), (480, 500))
            x, y = (i % 3) * 500, (i // 3) * 550
            sheet.paste(thumb, (x + (500-thumb.width)//2, y+30))
            draw.text((x+12, y+8), f"{start+i+1}. {label}", fill="black")
        sheet.save(target / f"sheet-{start//5+1}.jpg")
    (target / "inventory.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(target)

if __name__ == "__main__":
    main()
