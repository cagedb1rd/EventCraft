"""Runtime archive must retain executable resources without development galleries."""

import re

from scripts.package_skill import ROOT, markdown_for_archive, selected_files


def test_runtime_archive_retains_skill_resources_and_omits_large_campaigns():
    selected = set(selected_files())
    assert len([p for p in selected if p.parent == ROOT / "eventcraft/data/art"]) == 10
    assert ROOT / "examples/inputs/birthday.json" in selected
    assert ROOT / "assets/styles/style-profiles.json" in selected
    assert not any(p.is_relative_to(ROOT / "examples/visual-v3") for p in selected)
    skill = ROOT / "SKILL.md"
    for link in re.findall(r"\]\(([^)]+)\)", skill.read_text(encoding="utf-8")):
        if not link.startswith("http"):
            target = (ROOT / link).resolve()
            assert target in selected or any(p.is_relative_to(target) for p in selected)


def test_compact_docs_link_omitted_evidence_to_source_without_losing_local_contracts():
    selected = set(selected_files())
    text = markdown_for_archive(ROOT / "docs/style-gallery.md", selected)
    assert "](../examples/visual-v3/" not in text
    assert "https://github.com/cagedb1rd/EventCraft/blob/main/examples/visual-v3/" in text
    text = markdown_for_archive(ROOT / "SKILL.md", selected)
    assert "](references/image-generation.md)" in text
    full = set(selected_files(with_examples=True))
    assert ROOT / "examples/visual-v3/style-gallery.png" in full
    assert not any(p.is_relative_to(ROOT / "image") for p in full)
