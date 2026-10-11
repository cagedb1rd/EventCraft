# Maintainer release checklist

Use this checklist when preparing a release. Review fictional examples, notices and checks before publishing; maintainers choose the repository owner and visibility.

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
