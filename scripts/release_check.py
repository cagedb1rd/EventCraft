"""Check tracked-file boundaries, documentation links and obvious credential patterns."""

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    result = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True)
    files = [Path(p) for p in result.stdout.decode().split("\0") if p]
    problems = []
    for relative in files:
        if relative.parts[0] in {".venv", "output", "private", "tmp", "dist"} or relative.name == ".env":
            problems.append(f"Private/generated working path tracked: {relative}")
        path = ROOT / relative
        if path.suffix in {".py", ".md", ".json", ".toml", ".yml", ".yaml", ".txt"}:
            text = path.read_text(encoding="utf-8")
            if re.search(r"(?:sk-[A-Za-z0-9_-]{30,}|ghp_[A-Za-z0-9]{30,}|AKIA[A-Z0-9]{16})", text):
                problems.append(f"Potential credential in {relative}")
            if path.suffix == ".md" and relative.name != "EventCraft_Codex_OneShot_Brief_v3.md":
                for link in re.findall(r"\]\(([^)\s]+)\)", text):
                    if link.startswith(("http:", "https:", "#")):
                        continue
                    target = path.parent / link.split("#", 1)[0]
                    if not target.exists():
                        problems.append(f"Missing local link from {relative}: {link}")
    if problems:
        raise SystemExit("\n".join(problems))
    print(f"Release scope, obvious-secret scan and local links passed for {len(files)} tracked files")


if __name__ == "__main__":
    main()
