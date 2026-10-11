# Preparing a GitHub update

The existing remote is [cagedb1rd/EventCraft](https://github.com/cagedb1rd/EventCraft). This guide prepares version **1.1.0**; it does not create a repository, push a branch or publish a release automatically.

## Validate the exact source

```sh
python -m pip install -e '.[dev]'
python -m playwright install chromium
python -m ruff check eventcraft scripts tests
python scripts/validate_skill.py
python scripts/release_check.py
python -m pytest -q
```

Use the project virtual environment. CJK fonts must be installed on the test host. `release_check.py` inspects tracked and pending unignored files, obvious credential patterns, local Markdown links and the project's per-file size threshold. It cannot certify rights or detect every secret. Review `git diff`, `git status --short` and the eventual staged diff; do not stage unknown private files.

`/image/` is ignored and must remain untracked. Keep all 14 research files locally unchanged. Generated original art is stored separately. `.env`, `private/`, `output/`, `tmp/`, dependencies and `dist/` remain ignored. Inspect any other user data before adding it.

The source contains large fictional development galleries and inline-image HTML. The runtime archive below is intentionally smaller; a source push may still be large. Use the PNG/PDF Gallery index for GitHub viewing: GitHub does not execute the offline HTML previews.

## Build versioned assets

```sh
python -m build
python scripts/package_skill.py
# Optional complete development archive, not required for installation:
python scripts/package_skill.py --with-examples
python scripts/isolated_smoke.py
```

Expected default files:

- `dist/eventcraft-skill-1.1.0.zip`: complete runtime Agent Skill, guides, original preview art and input samples.
- `dist/eventcraft-1.1.0-py3-none-any.whl`: Python CLI.
- `dist/eventcraft-1.1.0.tar.gz`: source distribution with development materials; larger than the runtime archive.

The optional `eventcraft-skill-1.1.0-with-examples.zip` contains all development outputs. Do not accidentally attach an old 1.0.0 build. Rebuild after the final source/documentation edit. Archive links to omitted examples/evidence point to the repository; runtime guide links stay local. Generate SHA-256 checksums for the exact attachments being released. `dist/` is not part of a normal source commit.

## Update the existing repository

Inspect `git remote -v` and the current branch. Commit only reviewed changes, then push that branch to the existing `origin` when the maintainer is ready. Do not create a duplicate repository or change visibility as part of this update.

Check [GitHub Actions](https://github.com/cagedb1rd/EventCraft/actions) for the exact new commit. Local Windows acceptance does not prove Ubuntu CI passed. The historical report includes an earlier failing run; it is not the current CI status.

For a release, create tag `v1.1.0` from the intended verified commit and use [prepared release notes](release-notes-1.1.0.md). Attach the compact Skill ZIP and optionally the wheel/source distribution with checksums. Keep the release as a draft while required checks are unresolved. Verify downloaded attachments and hashes before publishing. A source-only GitHub update does not require a new Release.
