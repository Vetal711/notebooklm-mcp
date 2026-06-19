import sys
import json
import argparse
import asyncio
from mcp.server.fastmcp import FastMCP
from .config import config
from .logger import logger
from .client import client

# Initialize MCP server
mcp = FastMCP("NotebookLM")


async def startup_check():
    """
    Executed at server startup to verify configuration and CLI availability.
    """
    logger.info("=== Starting NotebookLM MCP Server v1.0.0 ===")
    logger.info("Configuration:")
    for k, v in config.get_summary().items():
        logger.info(f"  {k}: {v}")

    logger.info("Checking NotebookLM CLI availability and authentication...")
    health = await client.check_health()

    if health["status"] == "OK":
        logger.info("Health check passed: CLI is available and authenticated.")
    else:
        logger.error(f"Health check failed: {health['error']}")
        logger.warning(
            "Server will start, but requests may fail until the issue is resolved."
        )


@mcp.tool()
async def health_check() -> str:
    """Check the availability of the CLI and authentication status."""
    try:
        health = await client.check_health()
        return json.dumps(health, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Tool error in health_check: {str(e)}")
        return json.dumps({"status": "ERROR", "error": str(e)}, indent=2)


@mcp.tool()
async def list_notebooks() -> str:
    """Get a list of all NotebookLM notebooks."""
    try:
        return await client.list_notebooks()
    except Exception as e:
        logger.error(f"Tool error in list_notebooks: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def create_notebook(name: str) -> str:
    """
    Create a new notebook in NotebookLM.

    name: The name of the new notebook.
    """
    try:
        return await client.create_notebook(name)
    except Exception as e:
        logger.error(f"Tool error in create_notebook: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def delete_notebook(notebook_id: str) -> str:
    """
    Delete a notebook from NotebookLM.

    notebook_id: The ID or name of the notebook to delete.
    """
    try:
        return await client.delete_notebook(notebook_id)
    except Exception as e:
        logger.error(f"Tool error in delete_notebook: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def add_source(notebook_id: str, content: str, source_type: str = None) -> str:
    """
    Add a source (file, text, URL) to a notebook.

    notebook_id: The ID of the notebook.
    content: The content (URL, absolute file path, or raw text).
    source_type: Optional. Type of source (url, text, file, youtube). Auto-detected if omitted.
    """
    try:
        return await client.add_source(notebook_id, content, source_type)
    except Exception as e:
        logger.error(f"Tool error in add_source: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def list_sources(notebook_id: str) -> str:
    """Get a list of all sources in a specific notebook."""
    try:
        return await client.list_sources(notebook_id)
    except Exception as e:
        logger.error(f"Tool error in list_sources: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def get_source_text(notebook_id: str, source_id: str) -> str:
    """
    Get the full indexed text content of a specific source in a notebook.

    notebook_id: The ID of the notebook.
    source_id: The ID of the source (use list_sources to find it).
    """
    try:
        return await client.get_source_text(notebook_id, source_id)
    except Exception as e:
        logger.error(f"Tool error in get_source_text: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def ask_notebook(notebook_id: str, question: str) -> str:
    """
    Ask a natural language question to a specific NotebookLM notebook.

    notebook_id: The ID of the notebook.
    question: The question you want to ask based on the notebook's sources.
    """
    try:
        return await client.ask_notebook_sequenced(notebook_id, question)
    except Exception as e:
        logger.error(f"Tool error in ask_notebook: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def get_summary(notebook_id: str) -> str:
    """Get the AI-generated summary of the notebook."""
    try:
        return await client.get_summary_sequenced(notebook_id)
    except Exception as e:
        logger.error(f"Tool error in get_summary: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def get_history(notebook_id: str) -> str:
    """
    Get the full conversation history (Q&A) for a specific notebook.

    notebook_id: The ID of the notebook.
    """
    try:
        return await client.get_history(notebook_id)
    except Exception as e:
        logger.error(f"Tool error in get_history: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def generate_audio(notebook_id: str, prompt: str) -> str:
    """
    Generate an audio overview (podcast) from the notebook's sources.
    Note: This process can take several minutes to complete.

    notebook_id: The ID of the notebook.
    prompt: Instructions for the audio overview (e.g., "focus on chapter 3").
    """
    try:
        return await client.generate_audio(notebook_id, prompt)
    except Exception as e:
        logger.error(f"Tool error in generate_audio: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def generate_report(notebook_id: str, prompt: str) -> str:
    """
    Generate a written report (briefing doc, study guide, blog post) from the notebook.
    Note: This process can take several minutes to complete.

    notebook_id: The ID of the notebook.
    prompt: Instructions for the report (e.g., "write a study guide for a 5th grader").
    """
    try:
        return await client.generate_report(notebook_id, prompt)
    except Exception as e:
        logger.error(f"Tool error in generate_report: {str(e)}")
        return f"Error: {str(e)}"


def main():
    """Entry point for the package."""
    parser = argparse.ArgumentParser(description="NotebookLM MCP Server")
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport protocol to use (stdio or sse)",
    )
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="Host to bind to for SSE transport"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind to for SSE transport"
    )

    args = parser.parse_args()

    # We must run startup check. With FastMCP, running it synchronously via asyncio is fine
    # before we start the server block.
    asyncio.run(startup_check())

    if args.transport == "sse":
        logger.info(
            f"Starting MCP server on SSE transport at http://{args.host}:{args.port}"
        )
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        logger.info("Starting MCP server on STDIO transport")
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
