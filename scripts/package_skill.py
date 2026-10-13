"""Build a portable runtime Skill; large fictional galleries are opt-in."""

import argparse
import re
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/cagedb1rd/EventCraft/blob/main/"
CORE = ["eventcraft", "references", "agents", "assets/styles", "examples/inputs"]
FULL = ["assets", "docs", "examples", "tests", ".github", "scripts"]
FILES = ["SKILL.md", "LICENSE", "THIRD_PARTY_NOTICES.md", "pyproject.toml", "README.md",
         "README.en.md", "assets/event.schema.json", "docs/skill-usage.md"]
DEVELOPMENT_FILES = ["CONTRIBUTING.md", "CHANGELOG.md", ".env.example", ".gitignore",
                     ".gitattributes", "MANIFEST.in", "requirements-dev.lock"]


def selected_files(with_examples=False):
    selected = {ROOT / path for path in FILES + (DEVELOPMENT_FILES if with_examples else [])}
    for directory in CORE + (FULL if with_examples else []):
        selected.update(p for p in (ROOT / directory).rglob("*")
                        if p.is_file() and "__pycache__" not in p.parts)
    for path in selected:
        relative = path.relative_to(ROOT)
        assert not any(part in {"image", "private", "tmp", ".git", ".venv"} for part in relative.parts)
        assert path.suffix.lower() not in {".ttf", ".otf", ".woff", ".woff2"}
        assert path.name != ".env"
    return sorted(selected)


def markdown_for_archive(path, selected):
    """Keep runtime links local; point omitted gallery/evidence links to source."""
    def replace(match):
        link = match.group(1)
        if link.startswith(("http:", "https:", "#", "mailto:")):
            return match.group(0)
        target, _, fragment = link.partition("#")
        resolved = (path.parent / target).resolve()
        if resolved in selected or (resolved.is_dir() and any(p.is_relative_to(resolved) for p in selected)):
            return match.group(0)
        if not resolved.is_relative_to(ROOT):
            raise ValueError(f"External local documentation link: {path}: {link}")
        url = REPOSITORY + resolved.relative_to(ROOT).as_posix()
        return "](" + url + ("#" + fragment if fragment else "") + ")"
    return re.sub(r"\]\(([^)\s]+)\)", replace, path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-examples", action="store_true", help="Include complete development galleries/evidence")
    args = parser.parse_args()
    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    destination = ROOT / "dist"
    destination.mkdir(exist_ok=True)
    suffix = "-with-examples" if args.with_examples else ""
    archive_path = destination / f"eventcraft-skill-{version}{suffix}.zip"
    selected = selected_files(args.with_examples)
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in selected:
            name = "eventcraft/" + path.relative_to(ROOT).as_posix()
            if path.suffix == ".md" and not args.with_examples:
                archive.writestr(name, markdown_for_archive(path, set(selected)))
            else:
                archive.write(path, name)
    print(f"{archive_path} ({archive_path.stat().st_size / 1024**2:.1f} MiB)")


if __name__ == "__main__":
    main()
