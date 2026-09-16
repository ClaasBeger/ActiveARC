"""Where the checkout really lives.

The external datasets (P-ARC, ConceptARC-GEN) are sibling checkouts found by
walking up from this repository. That walk has to start at the *main* checkout:
inside a git worktree the code sits under ``.claude/worktrees/<name>/``, so
walking up from there lands in ``.claude`` and the siblings are invisible --
P-ARC silently resolves to no tasks rather than failing loudly.

A worktree's ``.git`` is a file pointing at ``<main>/.git/worktrees/<name>``,
which is enough to recover the main checkout without shelling out to git.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

_FRAMEWORK_DIR = Path(__file__).resolve().parent


def _main_checkout_from_worktree(root: Path) -> Optional[Path]:
    git_path = root / ".git"
    if not git_path.is_file():
        return None
    try:
        text = git_path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not text.startswith("gitdir:"):
        return None
    gitdir = Path(text.split(":", 1)[1].strip())
    # <main>/.git/worktrees/<name> -> <main>
    parts = gitdir.parts
    if "worktrees" in parts:
        idx = len(parts) - 1 - parts[::-1].index("worktrees")
        git_dir = Path(*parts[:idx])
        if git_dir.name == ".git":
            return git_dir.parent
    return None


def activearc_root() -> Path:
    """The repository root, resolved to the main checkout even from a worktree."""
    root = _FRAMEWORK_DIR.parent
    main = _main_checkout_from_worktree(root)
    return main if main is not None else root


ACTIVEARC_ROOT = activearc_root()

# Bundled data and vendored dependencies. Resolved against the main checkout
# because a worktree does not receive the repository's submodules: they are
# present but empty there, so verifiers living in one (the google code-golf
# slots, the only verifier for 19 ARC-AGI-1 tasks) silently vanish and those
# tasks report "no valid verifier" instead of raising.
EXTERNAL_DIR = ACTIVEARC_ROOT / "external"

