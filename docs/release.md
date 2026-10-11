# Maintainer release checklist

Use this checklist when preparing a release. Review fictional examples, notices and checks before publishing; maintainers choose the repository owner and visibility.

The public repository is [cagedb1rd/EventCraft](https://github.com/cagedb1rd/EventCraft). Its remote is already configured: use `git push origin main` for updates, rather than creating a second repository. Check [Actions](https://github.com/cagedb1rd/EventCraft/actions) before a stable release. The first Ubuntu run failed during tests; investigate the authenticated logs and fix it before claiming Linux acceptance.

1. Install and run `ruff check eventcraft scripts tests`, `python scripts/validate_skill.py`, `pytest -q`, `python -m build`.
2. Regenerate examples/Gallery when templates change; visually inspect the pairs and print PDFs.
3. `git status --short`; inspect `git diff --cached`; verify no `.env`, private input, credential, user reference or `output/` file is tracked. `python scripts/release_check.py` performs scope, link and obvious-secret checks.
4. Confirm the intended account/owner, repository visibility and remote URL with `git remote -v`. The suggested repository name is `eventcraft`.

Only when you are ready, with GitHub CLI installed/authenticated:

```sh
gh auth login
# Choose --private instead if that is your intention; this command publishes files.
gh repo create eventcraft --public --source . --remote origin --push
```

Or create the repository in GitHub's UI and use the exact URL GitHub gives you:

```sh
git remote add origin <YOUR_REPOSITORY_URL>
git push -u origin main
```

Inspect CI results after each push/PR. The committed verification report describes the environment actually tested; do not infer Linux/macOS, OCR or paid-API support from the Windows run alone. PyPI publication is a separate maintainer decision; build outputs are local under `dist/`. Generate the complete Skill archive with `python scripts/package_skill.py`, then attach it to a GitHub Release if desired. The archive includes runtime code/config and required references, excluding private outputs and dependencies. Because `dist/` is Git-ignored, these release artifacts are not included in a normal push.

## Upload release assets in the browser

1. Run `python scripts/package_skill.py` and `python -m build`. Rebuild after documentation/code changes so the attachments match the release commit.
2. Open [New release](https://github.com/cagedb1rd/EventCraft/releases/new), signed into the intended maintainer account. Create tag `v1.0.0` from the verified `main` commit and title it `EventCraft v1.0.0`.
3. Attach `dist/eventcraft-skill-1.0.0.zip`. This is the complete Agent Skill. Optionally attach `dist/eventcraft-1.0.0-py3-none-any.whl` and `dist/eventcraft-1.0.0.tar.gz` for Python users, plus `dist/SHA256SUMS.txt` for integrity checks. Do not attach private input or virtual environments.
4. Describe the ten styles, explainable three-way recommendations, generated deliverables, installation requirements and verified/unverified environments. The automatic **Source code** downloads do not replace the complete Skill ZIP.
5. While required CI checks remain unresolved, save a draft rather than publishing a stable release. Once checks pass and the notes accurately describe remaining limitations, publish the release. Confirm each attachment downloads and its SHA-256 matches the checksum file.
