#!/usr/bin/env bash
# Remove Co-Authored-By: Claude and "Generated with Claude Code" lines from every
# commit message in the repository, across every local branch.
#
# Rewrites history: every commit from the oldest affected one forward gets a new
# hash, so the branches have to be force-pushed afterwards and anyone else with a
# clone has to re-fetch. The original tips are saved as refs/original/* by
# filter-branch, and printed below, so the old history is recoverable until those
# refs are deleted.
#
# Run from the main checkout, not from a worktree: filter-branch has to move the
# main branch, and git refuses to move a branch that is checked out elsewhere.
#
#   bash scripts/strip_commit_coauthors.sh          # rewrite
#   bash scripts/strip_commit_coauthors.sh --push   # rewrite, then force-push
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

if [ -n "$(git status --porcelain)" ]; then
    echo "Working tree is dirty. Commit or set aside your changes first." >&2
    exit 1
fi

before=$(git log --branches --remotes --format='%H %(trailers:key=Co-Authored-By)' \
         | grep -c 'Co-Authored-By' || true)
echo "commits carrying the trailer, before: $before"
if [ "$before" = "0" ]; then
    echo "Nothing to do."
    exit 0
fi

echo "saving current branch tips to .git/coauthor-rewrite-backup.txt"
git for-each-ref --format='%(refname) %(objectname)' refs/heads \
    > .git/coauthor-rewrite-backup.txt

# --msg-filter reads each message on stdin and writes the replacement. Dropping
# the lines can leave a trailing blank line; git normalises that when it rebuilds
# the commit.
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --msg-filter '
    sed -e "/^Co-[Aa]uthored-[Bb]y: Claude/d" \
        -e "/^Co-[Aa]uthored-[Bb]y: .*@anthropic\.com>/d" \
        -e "/Generated with \[Claude Code\]/d"
' -- --all

# --branches --remotes, not --all: filter-branch parks the pre-rewrite tips under
# refs/original/, which --all would walk, so the count would never reach zero.
after=$(git log --branches --remotes --format='%H %(trailers:key=Co-Authored-By)' \
        | grep -c 'Co-Authored-By' || true)
echo "commits carrying the trailer, after: $after"
[ "$after" = "0" ] || { echo "Some survived -- not pushing." >&2; exit 1; }

if [ "${1:-}" = "--push" ]; then
    echo "force-pushing every branch"
    git push --force-with-lease origin --all
else
    echo
    echo "History rewritten locally. To publish:"
    echo "    git push --force-with-lease origin --all"
fi

echo
echo "Old history is still reachable under refs/original/ until you run:"
echo "    git for-each-ref --format='%(refname)' refs/original \\"
echo "      | xargs -n1 git update-ref -d"
