"""Build inspection sheets from real exported PNGs, never from template placeholders."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from eventcraft.recommendation import profiles

ROOT = Path(__file__).resolve().parents[1]

def main():
    target = ROOT / "docs/images"
    target.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGB", (2400, 1800), "#e0ddd5")
    draw = ImageDraw.Draw(sheet)
    for i, sid in enumerate(profiles()):
        with Image.open(ROOT / f"examples/gallery/{sid}/poster_portrait.png") as im:
            thumb = ImageOps.contain(im.convert("RGB"), (452, 820))
        x, y = i % 5 * 480, i // 5 * 900
        sheet.paste(thumb, (x + (480-thumb.width)//2, y+40))
        draw.text((x+12, y+14), sid, fill="black")
    sheet.save(target / "style-contact-sheet.png")
    sheet = Image.new("RGB", (2400, 1800), "#e0ddd5")
    draw = ImageDraw.Draw(sheet)
    for i, form in enumerate(["boarding-pass", "ticket-stub", "formal-card", "folded"]):
        with Image.open(ROOT / f"examples/gallery/invitations/{form}/invitation.png") as im:
            thumb = ImageOps.contain(im.convert("RGB"), (1140, 820))
        x, y = i % 2 * 1200, i // 2 * 900
        sheet.paste(thumb, (x + (1200-thumb.width)//2, y+40))
        draw.text((x+12, y+14), form, fill="black")
    sheet.save(target / "invitation-contact-sheet.png")
    print("Real poster and stationery inspection sheets saved")

if __name__ == "__main__":
    main()
