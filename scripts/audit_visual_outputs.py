"""Decode composed QRs, inspect PDF text and rasterize real print deliverables."""
import hashlib
import json
import subprocess
from pathlib import Path

import cv2
from PIL import Image, ImageDraw, ImageOps
from pypdf import PdfReader

from eventcraft.schema import Event, facts
from eventcraft.security import write_json

ROOT = Path(__file__).resolve().parents[1]


def compact(value):
    return ''.join(value.split())


def sheet(paths, target, columns, cell):
    width, height = cell
    canvas = Image.new("RGB", (width * columns, height * ((len(paths)+columns-1)//columns)), "#dedbd5")
    draw = ImageDraw.Draw(canvas)
    for i, (label, path) in enumerate(paths):
        with Image.open(path) as source:
            thumb = ImageOps.contain(source.convert("RGB"), (width-24, height-40))
        x, y = i % columns * width, i // columns * height
        canvas.paste(thumb, (x+(width-thumb.width)//2, y+30))
        draw.text((x+10, y+8), label, fill="black")
    canvas.save(target)


def main():
    target = ROOT / "tmp/visual-qa"
    target.mkdir(parents=True, exist_ok=True)
    detector = cv2.QRCodeDetector()
    qr_records, pdf_records = [], []
    for path in sorted((ROOT / "examples").rglob("manifest.json")):
        event = Event.model_validate_json(path.with_name("event.json").read_text(encoding="utf-8"))
        manifest = json.loads(path.read_text(encoding="utf-8"))
        for name in ["poster_portrait", "poster_square", "invitation", "invitation_outside"]:
            image = path.parent / (name + ".png")
            if not image.exists() or not event.registration_url or event.assets.qr_image:
                continue
            decoded, _, _ = detector.detectAndDecode(cv2.imread(str(image)))
            if decoded != event.registration_url:
                raise ValueError(f"QR failed in composed image: {image}")
            qr_records.append({"path": image.relative_to(ROOT).as_posix(), "decoded": decoded})
        for name in manifest["checks"]["pdf_pages"]:
            pdf = path.parent / name
            reader = PdfReader(pdf)
            text = compact(''.join(p.extract_text() or '' for p in reader.pages))
            if name not in {"invitation_outside.pdf"}:
                for field in ["title", "when", "where"]:
                    assert compact(facts(event)[field]) in text, f"PDF fact missing: {pdf}: {field}"
            prefix = target / (path.parent.relative_to(ROOT).as_posix().replace('/', '_') + "_" + pdf.stem)
            subprocess.run(["pdftoppm", "-r", "72", "-png", str(pdf), str(prefix)], check=True,
                           capture_output=True)
            previews = sorted(target.glob(prefix.name+"-*.png"))
            assert len(previews) == len(reader.pages)
            pdf_records.append({"path": pdf.relative_to(ROOT).as_posix(), "pages": len(reader.pages),
                                "page_mm": [[round(float(p.mediabox.width)*25.4/72, 2),
                                             round(float(p.mediabox.height)*25.4/72, 2)] for p in reader.pages],
                                "text_layer": bool(text), "poppler_rendered": True})
    originals = json.loads((ROOT / "tmp/reference-study/inventory.json").read_text(encoding="utf-8"))
    for record in originals:
        assert hashlib.sha256((ROOT / "image" / record["file"]).read_bytes()).hexdigest() == record["sha256"]
    square_paths = [(p.parent.name, p) for p in sorted((ROOT / "examples/gallery").glob("*/poster_square.png"))]
    sheet(square_paths, target / "square-inspection.png", 5, (330, 360))
    selected = [
        ("Web Summit A4", "examples_visual-v2_web-summit_poster_print-1.png"),
        ("Premium boarding pass", "examples_visual-v2_web-summit_invitation_print-1.png"),
        ("Boarding pass", "examples_gallery_invitations_boarding-pass_invitation_print-1.png"),
        ("Ticket stub", "examples_gallery_invitations_ticket-stub_invitation_print-1.png"),
        ("Formal card", "examples_gallery_invitations_formal-card_invitation_print-1.png"),
        ("Folded exterior", "examples_gallery_invitations_folded_invitation_folded_print-1.png"),
        ("Folded interior", "examples_gallery_invitations_folded_invitation_folded_print-2.png"),
    ]
    sheet([(label, target / filename) for label, filename in selected], target / "pdf-inspection.png", 3, (500, 680))
    write_json(ROOT / "docs/visual-audit.json", {"composed_qr_count": len(qr_records), "pdf_count": len(pdf_records),
        "references_unchanged": len(originals), "qr": qr_records, "pdf": pdf_records,
        "limits": "QR is a demo URL. PDF text/Poppler checks do not certify commercial print color."})
    print(f"Decoded {len(qr_records)} composed QRs; Poppler rendered {len(pdf_records)} PDFs; all 14 originals unchanged")


if __name__ == "__main__":
    main()
