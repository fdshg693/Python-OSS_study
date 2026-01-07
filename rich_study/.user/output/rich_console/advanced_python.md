# Advanced Python Techniques Demonstrated in `rich/console.py`

- **Protocols & runtime checks**: Uses `Protocol` and `runtime_checkable` (`ConsoleRenderable`, `RichCast`) to type-hint extensible rendering contracts without tight coupling.
- **Dataclasses with behavior**: `ConsoleOptions` is a `dataclass` carrying both configuration and helper methods (`update`, `copy`, `update_dimensions`) while keeping immutability via copy-on-write.
- **Sentinel objects**: `NoChange` / `NO_CHANGE` allow optional updates without `None` ambiguity, a clean pattern for optional argument updates.
- **Thread-local state**: `ConsoleThreadLocals` (inherits `threading.local`) isolates theme stacks and buffers per thread while sharing the console instance.
- **Context managers for modes**: Multiple custom context managers (`Capture`, `ThemeContext`, `PagerContext`, `ScreenContext`) encapsulate enter/exit lifecycles, including resource cleanup and buffer handling.
- **Composable generators**: Rendering leverages generator composition: `render` recurses through iterables yielding `Segment`s; `render_lines` slices via `itertools.islice` to honor `max_height`.
- **Higher-order decorators**: `group` decorator turns methods returning iterables into `Group` renderables, showing functional composition for layout.
- **Platform feature detection**: Lazy global cache for Windows console features; safe fallbacks via try/except imports and feature flags.
- **Rich type unions**: Extensive use of `Union`, `Optional`, `Literal`, and type aliases to clarify API contracts (`RenderableType`, `JustifyMethod`, `OverflowMethod`).
- **Performance micro-optimizations**: Local variable bindings (`_Segment = Segment`, `_append = list.append`) in hot paths; precomputed mappings (`_TERM_COLORS`, `_STYLE_MAP` in Style) to reduce lookup overhead.
- **Export pipeline**: Demonstrates structured serialization to HTML/SVG/text using style-aware rendering and cached CSS class generation, including unique IDs via Adler32 hashes.
- **Graceful IO handling**: Handles `BrokenPipeError`, Unicode errors, and Jupyter rendering specially; uses batched writes to sidestep CPython <3.11 32KB Windows write bug.
- **Design for testability**: `_environ` is injectable, and width/height can be overridden, enabling deterministic tests; `record=True` enables snapshot-based export assertions.
