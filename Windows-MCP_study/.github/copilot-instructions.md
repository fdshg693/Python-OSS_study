# Windows-MCP Copilot Instructions

## Project Overview
Windows-MCP is a Model Context Protocol (MCP) server that bridges AI agents with the Windows OS, enabling desktop automation via UI interaction, application control, and PowerShell execution. Built with FastMCP framework.

## Architecture

### Core Components
- **`main.py`** - MCP server entry point; defines all MCP tools (`App-Tool`, `State-Tool`, `Click-Tool`, etc.) using FastMCP decorators
- **`src/desktop/`** - Desktop interaction layer
  - `service.py` - `Desktop` class: app management, PowerShell execution, mouse/keyboard operations, window control
  - `views.py` - Data models: `DesktopState`, `App`, `Status` (window states)
  - `config.py` - Browser names, excluded apps, DPI settings
- **`src/tree/`** - UI Accessibility tree parsing
  - `service.py` - `Tree` class: crawls Windows UI Automation tree, extracts interactive/scrollable elements
  - `views.py` - `TreeState`, `TreeElementNode`, `ScrollElementNode`, `BoundingBox`, `Center`
  - `config.py` - Control type classifications (interactive, informative, structural)

### Data Flow
1. `State-Tool` → `Desktop.get_state()` → `Tree.get_state()` → parses UI Automation tree
2. Returns: active app, open apps, interactive elements (with coordinates), scrollable areas, optional screenshot
3. Other tools (`Click-Tool`, `Type-Tool`) use coordinates from State-Tool output

## Development

### Setup & Running
```powershell
# Install dependencies (requires Python 3.13+, UV package manager)
pip install uv
uv sync

# Run server (stdio transport - default)
uv run main.py

# Run with HTTP transport
uv run main.py --transport sse --host localhost --port 8000
```

### Transport Options
- `stdio` (default) - For Claude Desktop, Perplexity, Gemini CLI integration
- `sse` / `streamable-http` - For HTTP-based clients

## Code Patterns

### Adding New MCP Tools
Follow existing pattern in `main.py`:
```python
@mcp.tool(
    name="Tool-Name",
    description="Clear description for LLM consumption",
    annotations=ToolAnnotations(
        title="Human Title",
        readOnlyHint=True/False,      # Does it modify state?
        destructiveHint=True/False,   # Can it cause data loss?
        idempotentHint=True/False,    # Same result on repeat?
        openWorldHint=True/False,     # Interacts with external world?
    ),
)
def tool_name(param: Type) -> str:
    return desktop.method()  # Delegate to Desktop service
```

### Coordinate System
- All UI interactions use `[x, y]` screen coordinates
- Coordinates obtained from `State-Tool` output (element centers)
- Resolution capped at 1080p for vision features via scale factor

### UI Element Detection
Interactive elements defined in `src/tree/config.py`:
- `INTERACTIVE_CONTROL_TYPE_NAMES`: ButtonControl, EditControl, CheckBoxControl, etc.
- `INFORMATIVE_CONTROL_TYPE_NAMES`: TextControl, ImageControl, StatusBarControl
- Elements are labeled with indices for reference in tool calls

### PowerShell Execution
Commands are base64-encoded and run via `subprocess`:
```python
encoded = base64.b64encode(command.encode("utf-16le")).decode("ascii")
subprocess.run(["powershell", "-NoProfile", "-EncodedCommand", encoded], ...)
```

## Key Dependencies
- `fastmcp` - MCP server framework
- `uiautomation` - Windows UI Automation access
- `pyautogui` - Mouse/keyboard simulation  
- `pywinauto` - Window management
- `humancursor` / `live-inspect` - Cursor tracking
- `fuzzywuzzy` - Fuzzy app name matching

## Important Conventions
- Tool names use `Kebab-Case` with `-Tool` suffix
- All location parameters are `list[int]` with exactly 2 elements `[x, y]`
- `Desktop` class is singleton instantiated at module level in `main.py`
- Fail-safe disabled: `pg.FAILSAFE = False` (allows cursor in corners)
- Default pause between actions: `pg.PAUSE = 1.0` second

## Limitations
- English Windows language preferred (App-Tool depends on locale)
- Cannot select specific text within paragraphs (a11y tree limitation)
- Type-Tool designed for text input, not IDE coding
