# NotebookLM MCP Server v0.5

Production-ready, fully asynchronous Model Context Protocol (MCP) server for Google NotebookLM.

This server acts as a bridge between AI agents (like Claude Code, Cursor) and NotebookLM.

## Features

- **Asynchronous Execution**: Fully utilizes `asyncio` for high concurrency handling.
- **Robust Execution**: Wrap NotebookLM CLI commands with timeouts and proper error handling.
- **Thread Safety (Command Queue)**: Multiple simultaneous requests are queued safely via `asyncio.Lock()`.
- **Advanced MCP Tools**: Includes `create_notebook`, `delete_notebook`, `add_source`, `list_sources`, `get_source_text`, `generate_audio`, `generate_report`, and `get_history`.
- **Multi-language Support (i18n)**: All tool docstrings are in English, ensuring seamless compatibility with any LLM globally.
- **Network Mode (SSE Transport)**: Supports both Standard I/O (local) and SSE (network) transport protocols.
- **Retries & Caching**: Temporary CLI failures are retried automatically. Read operations are cached.
- **Centralized Configuration**: Managed via `.env` file with sensible defaults.
- **Diagnostics**: Built-in `health_check()` tool to verify CLI availability and authentication status.
- **Logging**: Rotating console and file logs (at `logs/notebooklm-mcp.log`), without duplication.
- **Docker & CI/CD Support**: Containerized for easy deployment and tested automatically via GitHub Actions (with auto PyPI publish).

## Installation

### Local Installation

The server is packaged as a standard Python module, meaning you can install it globally with a single command.

1. Install directly from this repository:
```bash
pip install -e .
```
*(If the repository is pushed to GitHub, users can do: `pip install git+https://github.com/your-username/notebooklm-mcp.git`)*

2. To support authentication, install the browser driver:
```bash
playwright install chromium
```

3. Copy the configuration template and customize if necessary:
```bash
cp .env.example .env
```

### Docker Deployment

To build and run via Docker:
```bash
docker build -t notebooklm-mcp .
docker run -i --rm -v ~/.notebooklm:/root/.notebooklm notebooklm-mcp
```
*(Note: You need to mount the `.notebooklm` config directory to share your local authentication session).*

## Configuration

Modify your `.env` file to customize:

- `NOTEBOOKLM_CLI`: The CLI command/path (default: `notebooklm`)
- `NOTEBOOKLM_TIMEOUT`: Command timeout in seconds (default: `180`)
- `LOG_LEVEL`: Logging detail level, e.g., `INFO`, `DEBUG`, `WARNING` (default: `INFO`)
- `LOG_FILE`: Path to the log file (default: `logs/notebooklm-mcp.log`)

## Authentication

Before running the server, ensure you are authenticated with NotebookLM:

```bash
notebooklm login
```

If your session expires, you will see authentication errors in the logs, and the `health_check` tool will report it.

## Running the Server

Because it is installed as a package, you can start the MCP server from anywhere by simply typing:

```bash
# Start locally using stdio transport (default)
notebooklm-mcp

# Start as a network server using SSE transport
notebooklm-mcp --transport sse --host 0.0.0.0 --port 8000
```

## Running Tests

To run the test suite:
```bash
pytest
```

The server will perform a startup health check and begin listening for MCP client connections.
