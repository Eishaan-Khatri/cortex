"""
CORTEX — Git Operations
Handles staging, committing, and branch management.
"""

import subprocess
import os


def run_git(args, cwd=None):
    """Run a git command and return (success, output)."""
    if cwd is None:
        cwd = os.path.dirname(os.path.dirname(__file__))

    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(f"  [GIT] Warning: {' '.join(args)} -> {result.stderr.strip()}")
        return result.returncode == 0, result.stdout.strip()
    except subprocess.TimeoutExpired:
        print(f"  [GIT] Timeout: {' '.join(args)}")
        return False, ""
    except FileNotFoundError:
        print("  [GIT] Error: git not found on PATH")
        return False, ""


def commit_file(filepath, message, cwd=None):
    """Stage and commit a single file."""
    run_git(["add", filepath], cwd=cwd)
    success, _ = run_git(["commit", "-m", message], cwd=cwd)
    if success:
        print(f"  [COMMIT] {message[:80]}")
    return success


def commit_files(filepaths, message, cwd=None):
    """Stage and commit multiple files."""
    for fp in filepaths:
        run_git(["add", fp], cwd=cwd)
    success, _ = run_git(["commit", "-m", message], cwd=cwd)
    if success:
        print(f"  [COMMIT] {message[:80]}")
    return success


def commit_all(message, cwd=None):
    """Stage all changes and commit."""
    run_git(["add", "-A"], cwd=cwd)
    success, _ = run_git(["commit", "-m", message], cwd=cwd)
    if success:
        print(f"  [COMMIT] {message[:80]}")
    return success


def commit_with_date(filepath, message, date_str, cwd=None):
    """
    Stage and commit a file with a specific author/committer date.
    Used for backfill operations.
    date_str format: "2024-01-15T12:00:00"
    """
    run_git(["add", filepath], cwd=cwd)

    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str

    try:
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=cwd or os.path.dirname(os.path.dirname(__file__)),
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def ensure_branch(branch_name, cwd=None):
    """Ensure a branch exists. Create it if it doesn't."""
    success, _ = run_git(["checkout", branch_name], cwd=cwd)
    if not success:
        run_git(["checkout", "-b", branch_name], cwd=cwd)


def switch_branch(branch_name, cwd=None):
    """Switch to a branch."""
    run_git(["checkout", branch_name], cwd=cwd)


def push(remote="origin", branch="main", cwd=None):
    """Push to remote."""
    success, output = run_git(["push", remote, branch], cwd=cwd)
    if success:
        print(f"  [PUSH] {remote}/{branch}")
    return success
