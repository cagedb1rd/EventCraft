# Maintainer release checklist

The requested scope is local preparation only. No GitHub repository creation, upload or visibility setting has been performed. Review fictional examples, notices and checks before publishing.

1. Install and run `ruff check eventcraft scripts tests`, `python scripts/validate_skill.py`, `pytest -q`, `python -m build`.
2. Regenerate examples/Gallery when templates change; visually inspect the pairs and print PDFs.
3. `git status --short`; inspect `git diff --cached`; verify no `.env`, private input, credential, user reference or `output/` file is tracked. `python scripts/release_check.py` performs scope, link and obvious-secret checks.
4. Choose the intended account/owner and repository visibility. The project name is `eventcraft`; there is no configured remote in this delivery.

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

CI runs on the first push/PR. Remote CI, Linux/macOS end-to-end behavior, real OCR and paid APIs are not proven by the local Windows run. PyPI publication is a separate maintainer decision; build outputs are local under `dist/`. Skill archive is generated separately with `python scripts/package_skill.py`, including runtime code/config and required references, excluding private outputs and dependencies.
