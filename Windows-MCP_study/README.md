**Windows MCP** is a lightweight, open-source project that enables seamless integration between AI agents and the Windows operating system. Acting as an MCP server bridges the gap between LLMs and the Windows operating system, allowing agents to perform tasks such as **file navigation, application control, UI interaction, QA testing,** and more.

mcp-name: io.github.CursorTouch/Windows-MCP

## Updates

- Windows-MCP is added to [MCP Registry](https://github.com/modelcontextprotocol/registry)
- Try out 🪟[Windows-Use](https://github.com/CursorTouch/Windows-Use)!!, an agent built using Windows-MCP.
- Windows-MCP is now featured as Desktop Extension in `Claude Desktop`.

### Supported Operating Systems

- Windows 7
- Windows 8, 8.1
- Windows 10
- Windows 11  

## ✨ Key Features

- **Seamless Windows Integration**  
  Interacts natively with Windows UI elements, opens apps, controls windows, simulates user input, and more.

- **Use Any LLM (Vision Optional)**
   Unlike many automation tools, Windows MCP doesn't rely on any traditional computer vision techniques or specific fine-tuned models; it works with any LLMs, reducing complexity and setup time.

- **Rich Toolset for UI Automation**  
  Includes tools for basic keyboard, mouse operation and capturing window/UI state.

- **Lightweight & Open-Source**  
  Minimal dependencies and easy setup with full source code available under MIT license.

- **Customizable & Extendable**  
  Easily adapt or extend tools to suit your unique automation or AI integration needs.

- **Real-Time Interaction**  
  Typical latency between actions (e.g., from one mouse click to the next) ranges from **0.7 to 2.5 secs**, and may slightly vary based on the number of active applications and system load, also the inferencing speed of the llm.

## 🛠️Installation

### Prerequisites

- Python 3.13+
- UV (Package Manager) from Astra, install with `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`
- `English` as the default language in Windows highly preferred or disable the `App-Tool` in the MCP Server for Windows with other languages.

<details>
  <summary>Install in Claude Desktop</summary>

  1. Install [Claude Desktop](https://claude.ai/download) and

```shell
npm install -g @anthropic-ai/mcpb
```

  2. Clone the repository.

```shell
git clone https://github.com/CursorTouch/Windows-MCP.git

cd Windows-MCP
```

  3. Build Desktop Extension `MCPB`:

```shell
npx @anthropic-ai/mcpb pack
```

  4. Open Claude Desktop:

Go to `Settings->Extensions->Advance Settings->Install Extension` (locate the `.mcpb` file)-> Install

  5. Enjoy 🥳.

For additional Claude Desktop integration troubleshooting, see the [MCP documentation](https://modelcontextprotocol.io/quickstart/server#claude-for-desktop-integration-issues). The documentation includes helpful tips for checking logs and resolving common issues.
</details>

<details>
  <summary>Install in Perplexity Desktop</summary>

  1. Install [Perplexity Desktop](https://apps.microsoft.com/detail/xp8jnqfbqh6pvf):

  2. Clone the repository.

```shell
git clone https://github.com/CursorTouch/Windows-MCP.git

cd Windows-MCP
```
  
  3. Open Perplexity Desktop:

Go to `Settings->Connectors->Add Connector->Advanced`

  4. Enter the name as `Windows-MCP`, then paste the following JSON in the text area.

```json
{
  "command": "uv",
  "args": [
    "--directory",
    "<path to the windows-mcp directory>",
    "run",
    "main.py"
  ]
}
```

5. Click `Save` and Enjoy 🥳.

For additional Claude Desktop integration troubleshooting, see the [Perplexity MCP Support](https://www.perplexity.ai/help-center/en/articles/11502712-local-and-remote-mcps-for-perplexity). The documentation includes helpful tips for checking logs and resolving common issues.
</details>

<details>
  <summary> Install in Gemini CLI</summary>

  1. Install Gemini CLI:

```shell
npm install -g @google/gemini-cli
```

  2. Clone the repository.

```shell
git clone https://github.com/CursorTouch/Windows-MCP.git

cd Windows-MCP
```

  3. Navigate to `%USERPROFILE%/.gemini` in File Explorer and open `settings.json`.

  4. Add the `windows-mcp` config in the `settings.json` and save it.

```json
{
  "theme": "Default",
  ...
//MCP Server Config
  "mcpServers": {
    "windows-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "<path to the windows-mcp directory>",
        "run",
        "main.py"
      ]
    }
  }
}
```

  5. Rerun Gemini CLI in terminal. Enjoy 🥳
</details>

<details>
  <summary>Install in Qwen Code</summary>
  1. Install Qwen Code:

```shell
npm install -g @qwen-code/qwen-code@latest
```
  2. Clone the repository.

```shell
git clone https://github.com/CursorTouch/Windows-MCP.git

cd Windows-MCP
```

  3. Navigate to `%USERPROFILE%/.qwen/settings.json`.

  4. Add the `windows-mcp` config in the `settings.json` and save it.

```json
{
//MCP Server Config
  "mcpServers": {
    "windows-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "<path to the windows-mcp directory>",
        "run",
        "main.py"
      ]
    }
  }
}
```

  5. Rerun Qwen Code in terminal. Enjoy 🥳
</details>

<details>
  <summary>Install in Codex CLI</summary>
  1. Install Codex CLI:

```shell
npm install -g @openai/codex
```
  2. Clone the repository.

```shell
git clone https://github.com/CursorTouch/Windows-MCP.git

cd Windows-MCP
```
  3. Navigate to `%USERPROFILE%/.codex/config.toml`.

  4. Add the `windows-mcp` config in the `config.toml` and save it.

```toml
[mcp_servers.windows-mcp]
command="uv"
args=[
  "--directory",
  "<path to the windows-mcp directory>",
  "run",
  "main.py"
]
```

  5. Rerun Codex CLI in terminal. Enjoy 🥳
</details>

---

## 🔨MCP Tools

MCP Client can access the following tools to interact with Windows:

- `Click-Tool`: Click on the screen at the given coordinates.
- `Type-Tool`: Type text on an element (optionally clears existing text).
- `Scroll-Tool`: Scroll vertically or horizontally on the window or specific regions.
- `Drag-Tool`: Drag from one point to another.
- `Move-Tool`: Move mouse pointer.
- `Shortcut-Tool`: Press keyboard shortcuts (`Ctrl+c`, `Alt+Tab`, etc).
- `Wait-Tool`: Pause for a defined duration.
- `State-Tool`: Combined snapshot of default language, browser, active apps and interactive, textual and scrollable elements along with screenshot of the desktop..
- `App-Tool`: To launch an application from the start menu, resize or move the window and switch between apps.
- `Shell-Tool`: To execute PowerShell commands.
- `Scrape-Tool`: To scrape the entire webpage for information.

## 🤝 Connect with Us
Stay updated and join our community:

- 📢 Follow us on [X](https://x.com/CursorTouch) for the latest news and updates

- 💬 Join our [Discord Community](https://discord.com/invite/Aue9Yj2VzS)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=CursorTouch/Windows-MCP&type=Date)](https://www.star-history.com/#CursorTouch/Windows-MCP&Date)

## ⚠️Caution

This MCP interacts directly with your Windows operating system to perform actions. Use with caution and avoid deploying it in environments where such risks cannot be tolerated.

## 🔒 Security

**Important**: Windows-MCP operates with full system access and can perform irreversible operations. Please review our comprehensive security guidelines before deployment.

For detailed security information, including:
- Tool-specific risk assessments
- Deployment recommendations
- Vulnerability reporting procedures
- Compliance and auditing guidelines

Please read our [Security Policy](SECURITY.md).

## 📝 Limitations

- Selecting specific sections of the text in a paragraph, as the MCP is relying on a11y tree. (⌛ Working on it.)
- `Type-Tool` is meant for typing text, not programming in IDE because of it types program as a whole in a file. (⌛ Working on it.)
- This MCP server can't be used to play video games 🎮.

## 🪪 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.