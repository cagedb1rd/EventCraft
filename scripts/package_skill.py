"""Create a relocatable skill archive, excluding private output and dependencies."""

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ["eventcraft", "scripts", "references", "assets", "agents", "docs", "examples", "tests", ".github"]
FILES = ["SKILL.md", "LICENSE", "THIRD_PARTY_NOTICES.md", "pyproject.toml", "README.md", "README.en.md", "CONTRIBUTING.md", "CHANGELOG.md", ".env.example", ".gitignore", ".gitattributes", "MANIFEST.in", "requirements-dev.lock"]


def main():
    destination = ROOT / "dist"
    destination.mkdir(exist_ok=True)
    archive_path = destination / "eventcraft-skill-1.0.0.zip"
    selected = [ROOT / path for path in FILES]
    selected += [p for directory in INCLUDE for p in (ROOT / directory).rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(set(selected)):
            archive.write(path, "eventcraft/" + path.relative_to(ROOT).as_posix())
    print(archive_path)


if __name__ == "__main__":
    main()
