# Implementation & Design Guides for `Console`

## Core design patterns
- **Protocol-driven rendering**: Accept any object implementing `__rich_console__` or `__rich__` (RichCast), falling back to strings. Keep render logic centralized in `Console.render` to ensure consistent Segment handling.
- **Immutable options snapshots**: Pass `ConsoleOptions` copies (`update`, `update_width/height`) down the render tree to avoid shared mutable state; this enables nested renderables to adapt width/height/overflow independently.
- **Segment-first pipeline**: Convert everything to `Segment`s early, then split/crop/pad at the boundary (`render_lines`, `_render_buffer`). This makes downstream output device agnostic.
- **Buffering & flushing discipline**: Use `_buffer` with `_enter_buffer` / `_exit_buffer` contexts to accumulate before writing, enabling capture/pager/export/live stacking without interleaving output.
- **Hooks & composition**: `RenderHook.process_renderables` lets features like `Live` inject cursor moves and overlays without coupling to `Console.print` internals.
- **Platform abstraction**: Guard ANSI usage; on legacy Windows, route through `_windows_renderer`. Respect `is_terminal`/`is_dumb_terminal` checks before emitting control codes.
- **Thread safety**: Guard shared state with `RLock`; keep `_record_buffer_lock` separate for export recording.
- **Graceful failure**: Catch `BrokenPipeError` in `_write_buffer` and call `on_broken_pipe` (exits with quiet mode and redirects stdout to devnull). Avoid recursion when max_width < 1.

## Adding new renderables
- Implement `__rich_console__(self, console, options)` yielding renderables or `Segment`s; consider adding `__rich_measure__` if custom sizing is needed.
- Honor width/height/overflow/justify/no_wrap from `ConsoleOptions`; avoid hard-coded widths. Prefer `measure_renderables` / `Segment.split_and_crop_lines` for wrapping.
- When adding options, extend `ConsoleOptions.update` to keep copying semantics and `NoChange` sentinel intact.

## Live/Progress integration
- Use `Console.set_live` / `_live_stack` to coordinate multiple live displays; the topmost live renders all nested ones via `Group`.
- `Live.process_renderables` prepends cursor reposition (`Control.home` or `LiveRender.position_cursor`) and appends the live renderable; ensure this remains idempotent per refresh.
- If adding heavy columns or renderables, set `ProgressColumn.max_refresh` to throttle recomputation.

## Export paths
- `record=True` is required for HTML/SVG/text export. Keep segment style fidelity; when adding new control flows, ensure recorded segments still pass through `_render_buffer`.
- SVG export caches style → CSS mappings; avoid mutating `Style` instances mid-render to keep cache hits consistent.

## Error handling & diagnostics
- When raising `NotRenderableError`, include type info. For style lookups, raise `MissingStyle` with parse context.
- Keep `_caller_frame_info` lightweight to avoid expensive `inspect.stack()` when `inspect.currentframe` suffices.

## Performance notes
- Avoid recomputing terminal size frequently; rely on `Console.size` caching `_width/_height` unless env vars override.
- `Segment.split_and_crop_lines` is hot; pass `pad=False` when padding is unnecessary. Use `Segment.apply_style` to batch-style segments instead of per-character styling.
- Prefer simple tuples and local variable binding (`_Segment = Segment`) in hot loops to reduce attribute lookups.
