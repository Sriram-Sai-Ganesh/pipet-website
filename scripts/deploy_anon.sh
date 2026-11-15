#!/usr/bin/env bash
# Build the anonymized site and force-push it as a single history-free commit
# authored by "Anonymous" to the given remote and branch. Point
# anonymous.4open.science at that branch to serve it at /w/<id>/.
#
# Usage: ANON_CODE_URL=... scripts/deploy_anon.sh <remote-name-or-url> [branch]
set -euo pipefail

remote="${1:?usage: deploy_anon.sh <remote-name-or-url> [branch]}"
branch="${2:-anon}"
root="$(cd "$(dirname "$0")/.." && pwd)"
# Resolve a remote name like "origin" from the main repo.
remote="$(git -C "$root" remote get-url "$remote" 2>/dev/null || echo "$remote")"

python3 "$root/scripts/build_anon.py"

cd "$root/dist-anon"
rm -rf .git
git init -q
git checkout -q -b "$branch"
git add -A
git -c user.name="Anonymous" -c user.email="anonymous@example.com" \
  commit -q -m "Update site"
git push -f "$remote" "$branch"
rm -rf .git
