"""Git operations — thin wrapper for branch management and push."""

from __future__ import annotations

import subprocess

import typer


def ensure_clean_tree() -> None:
    """Error if the working tree has uncommitted changes."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        typer.echo("Error: working tree has uncommitted changes. Commit or stash them first.")
        raise typer.Exit(code=1)


def checkout_or_create_branch(branch: str) -> None:
    """Check out the branch if it exists, otherwise create it."""
    # Check if branch already exists (local)
    result = subprocess.run(
        ["git", "rev-parse", "--verify", branch],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        subprocess.run(["git", "checkout", branch], check=True)
        typer.echo(f"Checked out existing branch: {branch}")
    else:
        subprocess.run(["git", "checkout", "-b", branch], check=True)
        typer.echo(f"Created and checked out new branch: {branch}")
