# CI checks

`.github/workflows/ci.yml` runs the `Makefile` commands from lines 91–103 on push; adjust those commands there to change what runs.

Set `USE_CHAT_CACHE=True` in `.env` to speed up the second pass of fixes.

# Rules

Global ignores are configured in `pyproject.toml`:

- ruff: `[tool.ruff.lint].ignore`
- mypy: `[tool.mypy]`

## Ruff rules

Ruff rules are easy to change; most issues can be auto-fixed.

For some rules you can suppress them locally in code with a comment, e.g. `# noqa E234,ANN001`.

Rules that are harder to fix:

- When catching exceptions, handle specific types instead of a blanket `Exception`.
- `subprocess` calls should validate that the command is safe first.
- …

Rule index: [Ruff rules](https://docs.astral.sh/ruff/rules/)

## Mypy rules

Mypy checks type annotations in Python. Fixes often require structural changes or edits across multiple files; auto-fix is less effective.

Local suppression: `# type: ignore`

Rule index: [Mypy error codes](https://mypy.readthedocs.io/en/stable/error_code_list.html)

# Possible optimizations

- Add an option to lint only certain directories.
- Add an edit mode that opens `vim` so the user can change the flagged code directly.
- Hide the `Original Code` section in the output and show only the fix diff, with `^^^^^^` under the lines where errors were found, to make fixes easier to review.
- Today fixes run linearly and then the user reviews; could move to background threads/processes with live terminal updates as each fix finishes.
- …
