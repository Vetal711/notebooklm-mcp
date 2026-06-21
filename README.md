# NotebookLM MCP Server v1.0

*Read this in other languages: [Русский](README_RU.md)*
Production-ready, fully asynchronous Model Context Protocol (MCP) server for Google NotebookLM.

This server acts as a bridge between AI agents (like Claude Desktop, Cursor, Antigravity) and NotebookLM, allowing your AI to read your notebooks, interact with your sources, and generate reports.

## Features

- **Asynchronous Execution**: Fully utilizes `asyncio` for high concurrency handling.
- **Robust Execution**: Wrap NotebookLM CLI commands with timeouts and proper error handling.
- **Thread Safety (Command Queue)**: Multiple simultaneous requests are queued safely via `asyncio.Lock()`.
- **Advanced MCP Tools**: Includes `create_notebook`, `delete_notebook`, `add_source`, `list_sources`, `get_source_text`, `generate_audio`, `generate_report`, and `get_history`.
- **Multi-language Support (i18n)**: All tool docstrings are in English, ensuring seamless compatibility with any LLM globally.
- **Network Mode (SSE Transport)**: Supports both Standard I/O (local) and SSE (network) transport protocols.
- **Retries & Caching**: Temporary CLI failures are retried automatically. Read operations are cached.
- **Diagnostics**: Built-in `health_check()` tool to verify CLI availability and authentication status.

---

## Installation

You can install this server either automatically (recommended) or manually.

### Method A: One-Click Automatic Install (Recommended)

This method automatically sets up a virtual environment, installs all dependencies (including `notebooklm-py` and Chromium for Playwright), and registers the server in your IDEs (Claude Desktop, Cursor, Antigravity).

1. Clone or download this repository:
   ```bash
   git clone https://github.com/Vetal711/notebooklm-mcp.git
   cd notebooklm-mcp
   ```

2. Run the auto-installer script:
   - **Windows**: Double-click `install.bat` (or run it in the terminal).
   - **Mac/Linux**: Run `bash install.sh`

3. Authenticate with Google:
   Once the installation is complete, you must authenticate the CLI. Run the following command and follow the instructions in the browser window:
   - **Windows**: `venv\Scripts\notebooklm.exe login`
   - **Mac/Linux**: `./venv/bin/notebooklm login`

4. Restart your IDE/Agent (Claude Desktop, Cursor, or Antigravity) and the server will be available!

---

### Method B: Manual Installation

If you prefer to configure everything manually or use a global Python environment:

1. Clone the repository:
   ```bash
   git clone https://github.com/Vetal711/notebooklm-mcp.git
   cd notebooklm-mcp
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\pip install -e .
   # On Mac/Linux:
   ./venv/bin/pip install -e .
   ```

3. Install the Playwright browser driver:
   ```bash
   # On Windows:
   venv\Scripts\playwright install chromium
   # On Mac/Linux:
   ./venv/bin/playwright install chromium
   ```

4. Authenticate:
   ```bash
   # On Windows:
   venv\Scripts\notebooklm.exe login
   # On Mac/Linux:
   ./venv/bin/notebooklm login
   ```

5. **Manual Configuration for MCP Clients**:
   Instead of running the automated configuration script, you can manually add the following JSON block to your MCP client's configuration file (e.g., `claude_desktop_config.json`, `cline_mcp_settings.json`, or `mcp_config.json`).
   
   *Make sure to replace `/absolute/path/to/notebooklm-mcp` with the actual absolute path to your cloned directory.*

   ```json
   {
     "mcpServers": {
       "NotebookLM": {
         "command": "/absolute/path/to/notebooklm-mcp/venv/bin/notebooklm-mcp",
         "args": []
       }
     }
   }
   ```
   *(Note for Windows users: Use `venv\\Scripts\\notebooklm-mcp.exe` and escape backslashes in paths).*

   **Important:** The server will automatically generate a `.env` file in the root folder on first run (or during installation) to handle absolute paths properly.

---

### Troubleshooting

**Error: `Authentication expired or invalid`**
If you receive this error in Claude/Cursor, it means the Playwright session's Google tokens have expired.
**Solution:**
1. Run the login command again: `venv\Scripts\notebooklm.exe login` (Windows) or `./venv/bin/notebooklm login` (Mac/Linux).
2. Ensure that your MCP client's configuration file (e.g., `claude_desktop_config.json`) includes the `"cwd": "/absolute/path/to/notebooklm-mcp"` parameter. This ensures the server always runs from the correct folder and doesn't lose the session.

---

### Docker Deployment

To build and run via Docker:
```bash
docker build -t notebooklm-mcp .
docker run -i --rm -v ~/.notebooklm:/root/.notebooklm notebooklm-mcp
```
*(Note: You need to mount the `.notebooklm` config directory to share your local authentication session).*
