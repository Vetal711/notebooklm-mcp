import asyncio
import time
from .config import config
from .logger import logger
from .exceptions import (
    AuthExpiredError,
    NotebookNotFoundError,
    CLIExecutionError,
    CLITimeoutError,
)


class NotebookLMClient:
    def __init__(self):
        self.cli_command = config.NOTEBOOKLM_CLI
        self.timeout = config.NOTEBOOKLM_TIMEOUT

        # Async lock for thread safety since CLI commands mutate global state
        self._lock = asyncio.Lock()

        # Simple TTL Cache for read operations
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes cache

    def _get_cache(self, key: str) -> str:
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["time"] < self._cache_ttl:
                return entry["data"]
            else:
                del self._cache[key]
        return None

    def _set_cache(self, key: str, data: str):
        self._cache[key] = {"time": time.time(), "data": data}

    async def _execute(
        self, args: list[str], max_retries: int, timeout_override: int = None
    ) -> str:
        """Inner execution logic without lock."""
        cmd_str = f"{self.cli_command} " + " ".join(
            f'"{a}"' if " " in a else a for a in args
        )
        attempt = 1
        effective_timeout = (
            timeout_override if timeout_override is not None else self.timeout
        )

        while attempt <= max_retries:
            logger.info(f"Executing [Attempt {attempt}/{max_retries}]: {cmd_str}")
            start_time = time.time()

            try:
                process = await asyncio.create_subprocess_exec(
                    self.cli_command,
                    *args,
                    stdin=asyncio.subprocess.DEVNULL,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(), timeout=effective_timeout
                    )
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                    execution_time = time.time() - start_time
                    logger.error(f"Timeout after {execution_time:.2f}s: {cmd_str}")

                    if attempt < max_retries:
                        attempt += 1
                        continue
                    else:
                        raise CLITimeoutError(
                            f"NotebookLM timeout after {effective_timeout} seconds."
                        )

                stdout_str = stdout.decode("utf-8").strip() if stdout else ""
                stderr_str = stderr.decode("utf-8").strip() if stderr else ""
                execution_time = time.time() - start_time

                if process.returncode != 0:
                    logger.error(
                        f"Command failed (Code {process.returncode}) after {execution_time:.2f}s: {cmd_str}"
                    )
                    if stderr_str:
                        logger.error(f"Stderr: {stderr_str}")

                    err_lower = stderr_str.lower()

                    if (
                        "unauthorized" in err_lower
                        or "login" in err_lower
                        or "expired" in err_lower
                    ):
                        raise AuthExpiredError()
                    if "not found" in err_lower:
                        raise NotebookNotFoundError(f"Resource not found: {stderr_str}")

                    if attempt < max_retries:
                        attempt += 1
                        await asyncio.sleep(1)
                        continue
                    else:
                        raise CLIExecutionError(
                            f"Command failed after {max_retries} attempts. Error: {stderr_str}"
                        )

                logger.info(f"Command success after {execution_time:.2f}s: {cmd_str}")
                return stdout_str

            except (
                AuthExpiredError,
                NotebookNotFoundError,
                CLITimeoutError,
                CLIExecutionError,
            ):
                raise
            except Exception as e:
                logger.error(f"Execution error for {cmd_str}: {str(e)}")
                raise CLIExecutionError(f"Failed to execute CLI: {str(e)}")

    async def run_command(
        self, args: list[str], max_retries: int = 2, timeout_override: int = None
    ) -> str:
        """Execute a single NotebookLM CLI command with locking."""
        async with self._lock:
            return await self._execute(args, max_retries, timeout_override)

    async def list_notebooks(self) -> str:
        cache_key = "list_notebooks"
        cached = self._get_cache(cache_key)
        if cached:
            logger.info("Returning cached list of notebooks")
            return cached

        result = await self.run_command(["list"])
        self._set_cache(cache_key, result)
        return result

    async def create_notebook(self, name: str) -> str:
        return await self.run_command(["create", name])

    async def delete_notebook(self, notebook_id: str) -> str:
        return await self.run_command(["delete", notebook_id])

    async def add_source(
        self, notebook_id: str, content: str, source_type: str = None
    ) -> str:
        args = ["source", "add", "-n", notebook_id]
        if source_type:
            args.extend(["--type", source_type])
        args.append(content)
        # File uploads can take time, overriding timeout slightly
        return await self.run_command(args, timeout_override=300)

    async def list_sources(self, notebook_id: str) -> str:
        return await self.run_command(["source", "list", "-n", notebook_id])

    async def get_source_text(self, notebook_id: str, source_id: str) -> str:
        # According to CLI docs: source fulltext <source_id> -n <notebook_id>
        return await self.run_command(
            ["source", "fulltext", source_id, "-n", notebook_id]
        )

    async def get_history(self, notebook_id: str) -> str:
        # notebooklm history -n <id> --show-all
        return await self.run_command(["history", "-n", notebook_id, "--show-all"])

    async def generate_audio(self, notebook_id: str, prompt: str) -> str:
        """Generate audio (podcast). Generation takes a long time, so we extend timeout to 600s."""
        async with self._lock:
            await self._execute(["use", notebook_id], max_retries=2)
            return await self._execute(
                ["generate", "audio", prompt], max_retries=1, timeout_override=600
            )

    async def generate_report(self, notebook_id: str, prompt: str) -> str:
        """Generate report. Generation takes a long time, so we extend timeout to 600s."""
        async with self._lock:
            await self._execute(["use", notebook_id], max_retries=2)
            return await self._execute(
                ["generate", "report", prompt], max_retries=1, timeout_override=600
            )

    async def ask_notebook_sequenced(self, notebook_id: str, question: str) -> str:
        """Safely switch notebook and ask question under a single lock."""
        async with self._lock:
            await self._execute(["use", notebook_id], max_retries=2)
            return await self._execute(["ask", question], max_retries=2)

    async def get_summary_sequenced(self, notebook_id: str) -> str:
        """Safely switch notebook and get summary under a single lock."""
        async with self._lock:
            await self._execute(["use", notebook_id], max_retries=2)
            return await self._execute(["summary"], max_retries=2)

    async def check_health(self) -> dict:
        status_info = {
            "status": "ERROR",
            "server": "NotebookLM MCP",
            "version": "1.0.0",
            "cli_available": False,
            "authenticated": False,
            "error": None,
        }
        try:
            await self.run_command(["list"], max_retries=1)
            status_info["cli_available"] = True
            status_info["authenticated"] = True
            status_info["status"] = "OK"
        except AuthExpiredError as e:
            status_info["cli_available"] = True
            status_info["error"] = str(e)
        except Exception as e:
            error_msg = str(e).lower()
            if (
                "not found" in error_msg
                or "is not recognized" in error_msg
                or "no such file" in error_msg
            ):
                status_info["error"] = "NotebookLM CLI not found. Is it installed?"
            else:
                status_info["cli_available"] = True
                status_info["error"] = str(e)
        return status_info


client = NotebookLMClient()
