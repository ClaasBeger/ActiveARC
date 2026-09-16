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

# Tracked changes only, which is what filter-branch itself refuses to run over.
# Not `git status --porcelain`: this repo carries hundreds of megabytes of
# untracked experiment output, and none of it is in filter-branch's way.
if ! git diff-index --quiet HEAD --; then
    echo "You have uncommitted changes to tracked files." >&2
    echo "Commit them or set them aside, then re-run." >&2
    exit 1
fi

before=$(git log --branches --format='%H %(trailers:key=Co-Authored-By)' \
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
# --branches, not --all. --all would also rewrite the refs/remotes/origin/*
# refs, which are this clone's record of where the server is. Rewriting them
# makes --force-with-lease compare the server against a value it has never held,
# and the push is rejected with "stale info". The local branches cover the whole
# history anyway, and the remote-tracking refs correct themselves on the push.
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --msg-filter '
    sed -e "/^Co-[Aa]uthored-[Bb]y: Claude/d" \
        -e "/^Co-[Aa]uthored-[Bb]y: .*@anthropic\.com>/d" \
        -e "/Generated with \[Claude Code\]/d"
' -- --branches

# --branches only, matching what was rewritten. Not --all: filter-branch parks
# the pre-rewrite tips under refs/original/, and the remote-tracking refs still
# point at the old commits until the push lands, so either would keep the count
# above zero no matter how well the rewrite went.
after=$(git log --branches --format='%H %(trailers:key=Co-Authored-By)' \
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
