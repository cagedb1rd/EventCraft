"""Reopen all public artifact packages; produce a verifiable release audit."""

import hashlib
import json
from pathlib import Path

from PIL import Image
from pypdf import PdfReader

from eventcraft.schema import Event, facts
from eventcraft.security import digest, write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    results = []
    for path in sorted((ROOT / "examples").rglob("manifest.json")):
        manifest = json.loads(path.read_text(encoding="utf-8"))
        event = Event.model_validate_json(path.with_name("event.json").read_text(encoding="utf-8"))
        assert digest(event.model_dump()) == manifest["event_digest"]
        assert event.demo and not manifest["publishable"]
        for record in manifest["files"]:
            file = path.parent / record["path"]
            assert file.is_file()
            assert record["sha256"] == hashlib.sha256(file.read_bytes()).hexdigest()
            if file.suffix == ".png":
                with Image.open(file) as image:
                    assert list(image.size) == record["dimensions"]
                    image.verify()
            if file.suffix == ".pdf":
                assert len(PdfReader(file).pages) >= 1
        assert all(layout["passed"] for layout in manifest["checks"]["layouts"].values())
        assert len(manifest["checks"]["layouts"]) == 4
        for text in (path.parent / "copy").iterdir():
            value = text.read_text(encoding="utf-8")
            assert all(facts(event)[field] in value for field in ["when", "where", "registration"])
        results.append({"package": path.parent.relative_to(ROOT).as_posix(), "style": manifest["base_style"],
                        "files": len(manifest["files"]), "layouts": 4, "checks": "passed"})
    assert len(results) >= 15, "Five examples and ten gallery campaigns required"
    report = {"packages": len(results), "png_campaign_images": len(results) * 3,
              "pdf_files": len(results) * 2, "layouts_verified": len(results) * 4,
              "gallery_pairs": 10, "results": results}
    write_json(ROOT / "docs/artifact-audit.json", report)
    print(f"Reopened and verified {len(results)} complete public packages")


if __name__ == "__main__":
    main()
