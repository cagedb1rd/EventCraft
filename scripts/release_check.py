"""Check tracked-file boundaries, documentation links and obvious credential patterns."""

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    result = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                            cwd=ROOT, capture_output=True, check=True)
    files = sorted({Path(p) for p in result.stdout.decode().split("\0") if p})
    problems = []
    for relative in files:
        if relative.parts[0] in {".venv", "output", "private", "tmp", "dist", "image"} or relative.name == ".env":
            problems.append(f"Private/generated working path tracked: {relative}")
        path = ROOT / relative
        if not path.is_file():
            continue
        if path.stat().st_size > 100 * 1024**2:
            problems.append(f"File exceeds this project's 100 MiB release threshold: {relative}")
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
    size = sum((ROOT / p).stat().st_size for p in files if (ROOT / p).is_file()) / 1024**2
    print(f"Release scope, obvious-secret scan and local links passed for {len(files)} Git candidates ({size:.1f} MiB)")
    if size > 500:
        print("Size advisory: source includes large development galleries; use the compact Skill ZIP for installation.")


if __name__ == "__main__":
    main()
