#!/usr/bin/env bash
# Manual publishing helper. This repository is never created automatically
# without a GitHub-authenticated CLI session under the owner's control.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OWNER_REPO="${1:-}"
if [[ -z "$OWNER_REPO" || "$OWNER_REPO" != */* ]]; then
  echo "Usage: bash scripts/publish_github.sh <owner>/<repo>" >&2
  exit 2
fi
for c in git gh; do
  command -v "$c" >/dev/null || { echo "Missing $c. Install GitHub CLI and authenticate with: gh auth login" >&2; exit 3; }
done
gh auth status >/dev/null || { echo "Authenticate first: gh auth login" >&2; exit 4; }
if gh repo view "$OWNER_REPO" >/dev/null 2>&1; then
  echo "Repository $OWNER_REPO already exists; refusing to overwrite or push blindly." >&2
  exit 5
fi
cd "$ROOT"
if [[ ! -d .git ]]; then
  git init -b main
fi
if [[ -n "$(git status --porcelain)" ]]; then
  git add -A
  git commit -m "Initial release: first-principles course PDF skill"
fi
gh repo create "$OWNER_REPO" --public --source=. --remote=origin --push
echo "Published: https://github.com/$OWNER_REPO"
