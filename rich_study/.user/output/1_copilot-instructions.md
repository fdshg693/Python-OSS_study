# Rich Copilot Instructions

- Scope: Rich is a terminal rendering library; core rendering lives in [rich/console.py](../../rich/console.py) with renderable protocols (`__rich_console__`, `__rich__`), `ConsoleOptions`, and `Segment`/`Theme` plumbing.
- Renderables: Implement `__rich_console__(console, options)` yielding `Segment`/`Text`/`ConsoleRenderable` or provide `__rich__` to adapt arbitrary objects ([rich/console.py](../../rich/console.py)). Use `measure_renderables` to size new renderables and honor `ConsoleOptions.min_width/max_width`.
- Text/Markup: Prefer `Text` for styled strings and `render_markup` for bbcode-style markup ([rich/text.py](../../rich/text.py), [rich/markup.py](../../rich/markup.py)). Respect `markup` and `highlight` flags when printing user-provided strings.
- Layout: Compose output with `Group`, `Align`, `Panel`, `Table`, and `Columns` renderables; keep them width-aware to avoid overflow in narrow terminals ([rich/layout.py](../../rich/layout.py), [rich/align.py](../../rich/align.py), [rich/table.py](../../rich/table.py), [rich/columns.py](../../rich/columns.py)).
- Live rendering: `Live` wraps a renderable with periodic refresh, optional alt-screen mode, and stdout/stderr redirection via `FileProxy` ([rich/live.py](../../rich/live.py)). `Live.renderable` stacks nested lives via an internal live stack; call `refresh()` under locks when updating.
- Progress: `Progress` builds on `Live` and `ProgressBar`, with columns driving the layout ([rich/progress.py](../../rich/progress.py), [rich/progress_bar.py](../../rich/progress_bar.py)). Use `track()` for simple iteration or `Progress.add_task/advance/update` for manual control; set `transient` to clear on exit.
- Jupyter: `JupyterMixin` enables widget-backed rendering when `is_jupyter` is true; gate imports of `ipywidgets`/IPython and warn if missing ([rich/jupyter.py](../../rich/jupyter.py), [rich/live.py](../../rich/live.py)).
- Windows: Console capability detection and color handling live in `_windows.py`/`_windows_renderer.py`; avoid regressions by keeping ANSI/no-ANSI paths tested.
- Filesystem/IO helpers: `file_proxy.py` wraps file-like objects to route writes through `Console`; `pager.py` provides system pager integration.

Developer workflows
- Env/setup: Use `poetry install` inside `poetry shell` ([CONTRIBUTING.md](../../CONTRIBUTING.md)). Optional extras: `poetry install -vv --with lint` for lint env (tox uses this).
- Tests: `make test` (or `pytest --cov-report term-missing --cov=rich tests/ -vv` without make) ([Makefile](../../Makefile), [CONTRIBUTING.md](../../CONTRIBUTING.md)). Tox targets `py38`–`py313` plus `lint`/`docs` ([tox.ini](../../tox.ini)).
- Type checking: `make typecheck` (or `mypy -p rich --no-incremental`) with strict settings (`[tool.mypy] strict = true`, see [pyproject.toml](../../pyproject.toml)). Add annotations for new code.
- Formatting: `make format` / `make format-check` (Black). `isort` profile is Black ([pyproject.toml](../../pyproject.toml)).
- Docs: From repo root `make docs` (or `cd docs; make html` after `pip install -r docs/requirements.txt`) ([CONTRIBUTING.md](../../CONTRIBUTING.md), [docs/Makefile](../../docs/Makefile)).
- CI parity: Tox runs `poetry install` before pytest and delegates lint to `make` to mirror GitHub Actions ([tox.ini](../../tox.ini)).

Conventions and patterns
- Favor clear names and docstrings; avoid abbreviations (per [CONTRIBUTING.md](../../CONTRIBUTING.md)).
- Rich is type-heavy: prefer `RenderableType`, `ConsoleRenderable`, `StyleType`, etc., rather than raw unions.
- When adding renderables, ensure `console.measure()` works and that `ConsoleOptions.height/width` are respected to prevent overflow in `Live`/progress displays.
- For logging/render hooks, push/pop via `Console.push_render_hook` and keep hooks exception-safe; `LogRender` handles time formatting ([rich/_log_render.py](../../rich/_log_render.py)).
- Tests live in `tests/`; new features should come with coverage, especially around wrapping/overflow and Windows capability detection.
- Examples in [examples/](../../examples) are runnable end-to-end; mirror their patterns for new demo scripts.

Release hygiene
- Update `CHANGELOG.md` and add to `CONTRIBUTORS.md` when appropriate.
- Pre-commit hooks are recommended (`pre-commit install`).