#!/usr/bin/env bash
set -euo pipefail
PACKAGE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-$HOME/Downloads/zyvro-product-finder-github}"
REMOTE="https://github.com/xansar1/zyvro-product-finder.git"
BRANCH="zyvro-v2-safe-demo"
if [ ! -d "$TARGET/.git" ]; then
  if [ -e "$TARGET" ]; then echo "Refusing to overwrite existing folder: $TARGET"; exit 1; fi
  git clone "$REMOTE" "$TARGET"
fi
cd "$TARGET"
ACTUAL="$(git remote get-url origin)"
case "$ACTUAL" in
  "$REMOTE"|"git@github.com:xansar1/zyvro-product-finder.git") ;;
  *) echo "Unexpected Git origin ($ACTUAL); aborting."; exit 2;;
esac
if [ -n "$(git status --porcelain)" ]; then
  echo "Git working tree has changes; stash/commit separately before installing. Nothing overwritten."
  exit 3
fi
git fetch origin main
if git show-ref --verify --quiet "refs/heads/$BRANCH" || git show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
  echo "Preview branch already exists. Avoiding overwrite; inspect before retry."
  exit 4
fi
git switch --create "$BRANCH" origin/main
for file in app.py README.md requirements.txt requirements-dev.txt .gitignore .env.example; do
  cp "$PACKAGE/$file" "$TARGET/$file"
done
mkdir -p zyvro scripts .streamlit .github/workflows
cp "$PACKAGE/zyvro/"*.py zyvro/
cp "$PACKAGE/scripts/"*.sh scripts/
cp "$PACKAGE/.streamlit/config.toml" "$PACKAGE/.streamlit/secrets.toml.example" .streamlit/
cp "$PACKAGE/.github/workflows/tests.yml" .github/workflows/
cp -R "$PACKAGE/tests" .
# Delete credential files ONLY on the new preview branch, never from the source package.
git rm -f --ignore-unmatch -- .env
rm -f .env
# V2's standalone app doesn't rely on old misleading legacy scripts or sample tables.
git rm -f --ignore-unmatch -- amazon_winning_products.py winning_products.csv
git add app.py README.md requirements.txt requirements-dev.txt .gitignore .env.example zyvro/ scripts/ .streamlit/config.toml .streamlit/secrets.toml.example .github/workflows/tests.yml tests/
if git diff --cached --name-only | grep -E '(^|/)\.env$|(^|/)secrets\.toml$' >/dev/null; then
  # A deletion of .env is expected. Ensure no tracked secret is added.
  if git diff --cached --diff-filter=A --name-only | grep -E '(^|/)\.env$|(^|/)secrets\.toml$' >/dev/null; then
    echo "Unsafe staged secrets; aborting"; exit 5
  fi
fi
if git diff --cached --quiet; then
  echo "No code changes to publish"; exit 0
fi
git commit -m "Build Zyvro V2 transparent product research demo"
git push -u origin "$BRANCH"
echo "Published preview branch: https://github.com/xansar1/zyvro-product-finder/tree/$BRANCH"
echo "Deploy this branch with main app file app.py on Streamlit Community Cloud."
