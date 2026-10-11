"""Persist an inspected host-generated image and its reproducible creative brief."""
import hashlib
import json
import shutil
import sys
from pathlib import Path

from eventcraft.visuals import systems

ROOT = Path(__file__).resolve().parents[1]

def main():
    style, source = sys.argv[1:]
    system = systems()[style]
    source = Path(source)
    target = ROOT / f"eventcraft/data/art/{style}.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    manifest = ROOT / "assets/generated-art.json"
    data = json.loads(manifest.read_text()) if manifest.exists() else {}
    data[style] = {"generator": "codex-imagegen", "prompt": system["art"],
                   "prompt_scope": "creative-brief-only",
                   "asset": f"eventcraft/data/art/{style}.png",
                   "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                   "reference_policy": "Original art based on design-language study; no reference embedded."}
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(style + " persisted")

if __name__ == "__main__":
    main()
