"""Forge CLI — PRD-driven development workflow orchestrator."""

from __future__ import annotations

from enum import Enum
from typing import Optional

import questionary
import typer

from forge.git import checkout_or_create_branch, ensure_clean_tree
from forge.github import GitHubSource
from forge.local import LocalSource
from forge.prompt import render_github_afk, render_github_once, render_local_afk, render_local_once
from forge.runner import run_afk_loop, run_interactive

app = typer.Typer(
    help="Forge — execute PRD-driven development workflows using Claude Code.",
    add_completion=False,
)


class Mode(str, Enum):
    once = "once"
    afk = "afk"


def _parse_iterations(value: Optional[str]) -> Optional[int | str]:
    """Parse --iterations value: positive integer or 'all'."""
    if value is None:
        return None
    if value == "all":
        return "all"
    try:
        n = int(value)
    except ValueError:
        raise typer.BadParameter(f"Must be a positive integer or 'all', got '{value}'")
    if n <= 0:
        raise typer.BadParameter(f"Must be a positive integer or 'all', got '{value}'")
    return n


def _pre_execution(suggested_branch: str) -> str:
    """Run pre-execution prompts and git checks. Returns the base branch."""
    ensure_clean_tree()

    branch = questionary.text(
        "Branch name:",
        default=suggested_branch,
    ).unsafe_ask()

    base_branch = questionary.text(
        "Base branch / PR target:",
        default="main",
    ).unsafe_ask()

    checkout_or_create_branch(branch)
    typer.echo("")

    return base_branch


def _validate_iterations(mode: Mode, iterations_raw: Optional[str]) -> Optional[int | str]:
    """Validate and parse iterations flag for the given mode."""
    iterations = _parse_iterations(iterations_raw)

    if mode == Mode.afk and iterations is None:
        raise typer.BadParameter(
            "--iterations / -i is required when mode is 'afk'."
        )

    # In once mode, silently ignore iterations
    if mode == Mode.once:
        iterations = None

    return iterations


@app.command()
def spec(
    name: str = typer.Argument(help="Name of the local spec (looks in .forge/<name>/)."),
    mode: Mode = typer.Option(
        ...,
        "--mode",
        "-m",
        help="Execution mode: 'once' (interactive) or 'afk' (autonomous).",
    ),
    iterations: Optional[str] = typer.Option(
        None,
        "--iterations",
        "-i",
        help="Number of issues to process, or 'all'. Required for afk mode.",
    ),
) -> None:
    """Execute issues from a local spec."""
    parsed_iterations = _validate_iterations(mode, iterations)

    source = LocalSource(name)
    _base_branch = _pre_execution(f"feature/{name}")

    if mode == Mode.once:
        issue = source.get_next_issue()

        if issue is None:
            typer.echo("All issues complete!")
            raise typer.Exit()

        remaining, total = source.get_remaining_count()
        typer.echo(f"Issue {issue.number}: {issue.filename}")
        typer.echo(f"Remaining: {remaining}/{total}")
        typer.echo("")

        prompt = render_local_once(
            prd_content=source.get_prd_content(),
            issue_number=issue.number,
            issue_filename=issue.filename,
            issue_content=issue.content,
            spec_dir=str(source.spec_dir),
        )
        run_interactive(prompt)

    elif mode == Mode.afk:
        prd_content = source.get_prd_content()
        run_afk_loop(
            source=source,
            iterations=parsed_iterations,
            render_prompt=lambda issue: render_local_afk(
                prd_content=prd_content,
                issue_number=issue.number,
                issue_filename=issue.filename,
                issue_content=issue.content,
            ),
            display_name=lambda issue: issue.filename,
        )


@app.command()
def prd(
    number: int = typer.Argument(help="GitHub PRD issue number."),
    mode: Mode = typer.Option(
        ...,
        "--mode",
        "-m",
        help="Execution mode: 'once' (interactive) or 'afk' (autonomous).",
    ),
    iterations: Optional[str] = typer.Option(
        None,
        "--iterations",
        "-i",
        help="Number of issues to process, or 'all'. Required for afk mode.",
    ),
) -> None:
    """Execute issues from a GitHub PRD."""
    parsed_iterations = _validate_iterations(mode, iterations)

    source = GitHubSource(number)
    _base_branch = _pre_execution(f"prd/{number}")

    if mode == Mode.once:
        issue = source.get_next_issue()

        if issue is None:
            typer.echo("All issues complete!")
            raise typer.Exit()

        remaining, total = source.get_remaining_count()
        typer.echo(f"Issue #{issue.number}: {issue.title}")
        typer.echo(f"Remaining: {remaining}/{total}")
        typer.echo("")

        prompt = render_github_once(
            prd_content=source.get_prd_content(),
            issue_number=issue.number,
            issue_title=issue.title,
            issue_content=issue.body,
        )
        run_interactive(prompt)

    elif mode == Mode.afk:
        prd_content = source.get_prd_content()
        run_afk_loop(
            source=source,
            iterations=parsed_iterations,
            render_prompt=lambda issue: render_github_afk(
                prd_content=prd_content,
                issue_number=issue.number,
                issue_title=issue.title,
                issue_content=issue.body,
            ),
            display_name=lambda issue: issue.title,
        )
