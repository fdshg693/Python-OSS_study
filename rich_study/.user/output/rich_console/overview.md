# rich/console.py Overview

- Role: central console abstraction that renders Rich renderables to stdout/stderr/Jupyter, manages sizing, styles, buffering, and export.
- Key classes: `Console`, `ConsoleOptions` (render options snapshot), `ConsoleDimensions`, protocol helpers (`ConsoleRenderable`, `RichCast`), context helpers (`Capture`, `PagerContext`, `ScreenContext`, `ThemeContext`).
- Core flow: `Console.print` → collect renderables and options → `Console.render` → recursively produce `Segment`s → buffer → `_write_buffer` writes to terminal, Jupyter, or file with platform-aware paths (Windows legacy renderer vs ANSI).
- Measurement: `Console.measure` and `render_lines` use `Measurement` and `Segment.split_and_crop_lines` to wrap/pad/crop respecting width/height/overflow and ascii_only detection.
- Environment handling: detects Jupyter, color system, terminal width/height, legacy Windows VT support; honors `FORCE_COLOR`, `NO_COLOR`, `COLUMNS`, `LINES`, `TTY_COMPATIBLE`, `FORCE_COLOR`, `TTY_INTERACTIVE`.
- Thread safety & live rendering: RLock around critical sections; live stack integrates with `Live` to coordinate cursor positioning and progress updates; render hooks allow injection (`RenderHook.process_renderables`).
- Recording & export: with `record=True`, buffers segments for later HTML/SVG/text export. SVG export computes geometry from recorded segments, caches styles, and can inline link metadata.
- Controls & screens: uses `Control` segments to move cursor, toggle alt-screen, set title, clear, show/hide cursor; `ScreenContext` wraps alt-screen use; `update_screen` writes partial screen regions.
- Logging helpers: `log` builds renderables via `_log_render` and optionally logs locals via `render_scope`, with linkable paths when supported.
- Input/IO: `input` wrapper (with prompt rendering), `bell`, `status` helper, `rule`, `print_json`, `pager` integration.
- Extensibility: renderables conform to `__rich_console__(console, options)`, cast via `rich_cast`; options can be updated/copy to adjust width/height/markup/highlight/overflow/justification per render.
