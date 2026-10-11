"""Portable format/resource validation used in CI, not behavioral proof."""

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
raw = (ROOT / "SKILL.md").read_text(encoding="utf-8")
frontmatter = re.match(r"\A---\n(.*?)\n---\n", raw, re.S)
assert frontmatter, "Missing YAML frontmatter"
data = yaml.safe_load(frontmatter[1])
assert data["name"] == "eventcraft"
assert isinstance(data["description"], str) and 20 <= len(data["description"]) <= 1024
for link in re.findall(r"\]\(([^)]+)\)", raw):
    if not link.startswith("http"):
        assert (ROOT / link).exists(), f"Broken resource: {link}"
meta = yaml.safe_load((ROOT / "agents/openai.yaml").read_text(encoding="utf-8"))
assert "$eventcraft" in meta["interface"]["default_prompt"]
assert len(meta["interface"]["short_description"]) in range(25, 65)
print("Skill format, metadata and resource links passed")
