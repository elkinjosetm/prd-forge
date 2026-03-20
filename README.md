# Orchestrator

Shell scripts that drive PRD-driven development with Claude Code. You write the spec, ralph executes the issues one by one.

## Workflow

1. **`/grill-me`** — Stress-test your idea. Get grilled on the plan until it's solid.
2. **`/write-a-prd`** — Turn the validated idea into a PRD with clear scope, constraints, and architecture.
3. **`/prd-to-issues`** — Break the PRD into independently-grabbable issues (local markdown files or GitHub sub-issues).
4. **`ralph-once` / `ralph-afk`** — Execute the issues sequentially with Claude Code.

Steps 1–3 are Claude Code skills that ship in this repo under `skills/`. Step 4 uses the shell scripts at the repo root.

## Scripts

### `ralph-once`

Picks the next incomplete issue, spawns a Claude Code session to implement it, and stops. Interactive mode — you see Claude work in real time.

```sh
# Local mode — issues as markdown files
ralph-once --spec ./specs/my-feature

# GitHub mode — issues as GitHub sub-issues
ralph-once --prd 42
```

### `ralph-afk`

Same as `ralph-once`, but loops through multiple issues autonomously. Non-interactive — pipe it to a log and walk away.

```sh
# Run 5 issues then stop
ralph-afk --spec ./specs/my-feature --iterations 5

# Run until all issues are done
ralph-afk --prd 42 --iterations all
```

Prints timing stats per iteration and a session summary at the end.

## Modes

### Local mode (`--spec <dir>`)

Expects a spec directory with this structure:

```
specs/my-feature/
├── prd.md              # The full PRD
├── issues/
│   ├── 01-setup.md     # Issue files, numbered for ordering
│   ├── 02-core.md
│   └── 03-api.md
├── config.json         # Optional: branch name and commit prefix
├── status.json         # Auto-created: tracks completed issues
└── progress.txt        # Auto-created: timestamped completion log
```

**`config.json`** (optional):
```json
{
  "branch": "feature/my-feature",
  "commitPrefix": "my-feature"
}
```

- `branch` — git branch to check out before running. Created if it doesn't exist.
- `commitPrefix` — commit messages become `<prefix> :: <description>`. If omitted, uses the spec directory name. Set to `null` to let the issue's acceptance criteria define the commit format.

### GitHub mode (`--prd <number>`)

Works with GitHub issues instead of local files:

- The PRD is a GitHub issue labeled `prd`
- Tasks are sub-issues of the PRD
- Progress is tracked by issue state (open/closed)
- A branch `prd/<number>` is created automatically

## Skills

The `skills/` directory contains Claude Code skills for steps 1–3 of the workflow. Install them by symlinking into your Claude Code skills directory:

```sh
ln -s /path/to/orchestrator/skills/grill-me ~/.claude/skills/grill-me
ln -s /path/to/orchestrator/skills/write-a-prd ~/.claude/skills/write-a-prd
ln -s /path/to/orchestrator/skills/prd-to-issues ~/.claude/skills/prd-to-issues
```

Once linked, they're available as `/grill-me`, `/write-a-prd`, and `/prd-to-issues` in any Claude Code session.

## Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) — `claude` must be in your PATH
- [GitHub CLI](https://cli.github.com/) — `gh`, authenticated. Only needed for GitHub mode.
- Python 3 — used for local mode bookkeeping
