# Guidelines for coding agents

`valohai-cli` is the `vh` command-line client for Valohai: Python 3.10+, Click, `requests`.

## Layout and tooling

- Commands live in `valohai_cli/commands/`, one module per command, with tests mirrored under `tests/commands/`.
  Copy the structure of a neighbouring command.
- Run tests with `uv run --extra=test pytest` (or `make test`),
  and linters with `make lint` (pre-commit: ruff, mypy, typos).
  Get both green before finishing.
- Talk to the API through `valohai_cli.api.request`, print through `valohai_cli.messages` and `valohai_cli.table`,
  and raise the exceptions in `valohai_cli.exceptions` for user-facing errors.
- Every command and option needs help text; a test enforces it.
- Tests invoke commands with the `runner` fixture and fake HTTP with `requests_mock`.
  Reuse the fixtures in `tests/conftest.py` and the data in `tests/fixtures/`.

## Scope

- Do only what the task asks: no speculative options, abstractions or drive-by fixes.
  Mention unrelated problems in your summary instead of fixing them.
- Don't touch lines you aren't changing (no reformatting or import reordering).
- Look for an existing helper, fixture or constant before writing one, and follow established patterns.
- Delete what your change makes unused.
  No commented-out code or debug output.
- Don't add a dependency for what the stdlib or an existing dependency already does.
- Existing commands, options and output formats are a public interface.
  Don't rename or remove them unless that is the task; add alongside.

## Code

- Fail loudly on broken contracts; don't return `None` or log and continue.
  Never swallow exceptions: catch the narrowest type around only the failing code.
- Parse external input (API responses, user config, `valohai.yaml`) tolerantly at the boundary;
  past it, trust the types and access required data directly.
- `0`, `""` and `[]` are values: test for `None` explicitly.
- Error messages name what failed, include the bad value, and say how to fix it.
  Never print tokens or other secrets.
- Avoid `Any`, and don't add `noqa` or `type: ignore` to get green; restructure instead.
- Flags and optional parameters are keyword-only.
  Prefer early returns to nesting.
- Comment only the non-obvious why.
  No docstrings that restate the name, except Click command docstrings, which are the help text.

## Tests

- Write the fewest tests that prove the change, and extend an existing test before adding a sibling.
  Branch coverage is not a goal.
- Test through the command and assert what the user sees or what request was sent.
- For a bug fix, confirm the test fails without the fix.
- Mock only HTTP and other external boundaries, never our own code.
  No sleeps or real network.
- Change an existing assertion only when the task changes that behaviour, and say so.

## Commits and PRs

- One logical change per commit, with refactors and renames in separate, earlier commits.
  One topic per PR, rebased on `master`.
- Commit subjects are imperative and accurate.
- The PR description says why the change exists, lists every behaviour change, and says how you tested it.
