"""Verify installed wheel code/config outside source cwd and a portable skill archive."""

import json
import os
import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]


def main():
    workspace = ROOT / f"tmp/isolated-{VERSION}"
    workspace.mkdir(parents=True, exist_ok=True)
    target = workspace / "wheel"
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "--no-deps", "--no-index", "--target", str(target),
                    str(ROOT / f"dist/eventcraft-{VERSION}-py3-none-any.whl")], check=True, capture_output=True)
    env = {**os.environ, "PYTHONPATH": str(target), "PYTHONIOENCODING": "utf-8"}
    import_check = subprocess.run([sys.executable, "-c", "import eventcraft; print(eventcraft.__file__)"],
                                  cwd=workspace, env=env, check=True, capture_output=True)
    assert str(target).lower() in import_check.stdout.decode().lower()
    subprocess.run([sys.executable, "-m", "eventcraft", "all", str(ROOT / "examples/inputs/lecture.json"),
                    "--auto-style", "--output", str(workspace / "wheel-campaign")], cwd=workspace,
                   env=env, check=True, capture_output=True)
    manifest = json.loads((workspace / "wheel-campaign/manifest.json").read_text(encoding="utf-8"))
    assert manifest["checks"]["png_dimensions"]
    assert manifest["artwork"]["provenance"] == "bundled-original-art"
    assert len(list((target / "eventcraft/data/art").glob("*.png"))) == 10
    assert (workspace / "wheel-campaign/invitation_print.pdf").is_file()
    with zipfile.ZipFile(ROOT / f"dist/eventcraft-skill-{VERSION}.zip") as archive:
        assert not any(".." in Path(p).parts for p in archive.namelist())
        assert not any(p.startswith("eventcraft/image/") for p in archive.namelist())
        assert len([p for p in archive.namelist() if p.startswith("eventcraft/eventcraft/data/art/") and p.endswith(".png")]) == 10
        archive.extractall(workspace / "skill")
    skill = workspace / "skill/eventcraft"
    assert (skill / "SKILL.md").is_file() and (skill / "assets/styles/style-profiles.json").is_file()
    subprocess.run([sys.executable, "-m", "eventcraft", "all", "examples/inputs/birthday.json", "--auto-style",
                    "--output", "output/portable-smoke"], cwd=skill, check=True, capture_output=True,
                   env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONPATH": str(skill)})
    print("Installed wheel and relocated complete skill both rendered a campaign")


if __name__ == "__main__":
    main()
