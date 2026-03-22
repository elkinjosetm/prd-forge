"""Forge CLI — PRD-driven development workflow orchestrator."""

from enum import Enum
from typing import Optional

import typer

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


def _validate_and_report(
    source: str,
    identifier: str | int,
    mode: Mode,
    iterations_raw: Optional[str],
) -> None:
    """Validate flag combinations and print parsed args (placeholder for execution)."""
    iterations = _parse_iterations(iterations_raw)

    if mode == Mode.afk and iterations is None:
        raise typer.BadParameter(
            "--iterations / -i is required when mode is 'afk'."
        )

    # In once mode, silently ignore iterations
    if mode == Mode.once:
        iterations = None

    typer.echo(f"Source:     {source}")
    typer.echo(f"Identifier: {identifier}")
    typer.echo(f"Mode:       {mode.value}")
    if mode == Mode.afk:
        typer.echo(f"Iterations: {iterations}")


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
    _validate_and_report("spec", name, mode, iterations)


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
    _validate_and_report("prd", number, mode, iterations)
