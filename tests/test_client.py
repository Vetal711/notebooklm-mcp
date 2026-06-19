import pytest
import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))
from unittest.mock import patch, MagicMock, AsyncMock
from notebooklm_mcp.client import NotebookLMClient
from notebooklm_mcp.exceptions import AuthExpiredError, CLIExecutionError


@pytest.fixture
def client():
    # Make sure we don't carry over cache between tests
    client = NotebookLMClient()
    client._cache = {}
    # Decrease timeout for testing
    client.timeout = 1
    return client


@pytest.mark.asyncio
@patch("asyncio.create_subprocess_exec")
async def test_run_command_success(mock_exec, client):
    mock_process = AsyncMock()
    mock_process.returncode = 0
    mock_process.communicate.return_value = (b"Success", b"")
    mock_exec.return_value = mock_process

    result = await client.run_command(["list"])
    assert result == "Success"
    assert mock_exec.call_count == 1


@pytest.mark.asyncio
@patch("asyncio.create_subprocess_exec")
async def test_run_command_retry_on_timeout(mock_exec, client):
    mock_process_timeout = AsyncMock()
    mock_process_timeout.communicate.side_effect = asyncio.TimeoutError()

    mock_process_success = AsyncMock()
    mock_process_success.returncode = 0
    mock_process_success.communicate.return_value = (b"Success", b"")

    mock_exec.side_effect = [mock_process_timeout, mock_process_success]

    result = await client.run_command(["list"])
    assert result == "Success"
    assert mock_exec.call_count == 2


@pytest.mark.asyncio
@patch("asyncio.create_subprocess_exec")
async def test_run_command_fatal_error(mock_exec, client):
    mock_process = AsyncMock()
    mock_process.returncode = 1
    mock_process.communicate.return_value = (b"", b"Unauthorized: please login")
    mock_exec.return_value = mock_process

    with pytest.raises(AuthExpiredError):
        await client.run_command(["list"])

    assert mock_exec.call_count == 1


@pytest.mark.asyncio
@patch("asyncio.create_subprocess_exec")
async def test_cache_list_notebooks(mock_exec, client):
    mock_process = AsyncMock()
    mock_process.returncode = 0
    mock_process.communicate.return_value = (b"Notebook 1\nNotebook 2", b"")
    mock_exec.return_value = mock_process

    res1 = await client.list_notebooks()
    assert res1 == "Notebook 1\nNotebook 2"
    assert mock_exec.call_count == 1

    res2 = await client.list_notebooks()
    assert res2 == "Notebook 1\nNotebook 2"
    assert mock_exec.call_count == 1
