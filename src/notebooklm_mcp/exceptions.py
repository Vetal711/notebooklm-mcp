class NotebookLMError(Exception):
    """Base exception for NotebookLM MCP Server errors."""

    pass


class AuthExpiredError(NotebookLMError):
    """Raised when the CLI reports that authentication has expired or is invalid."""

    def __init__(
        self, message="Authentication expired. DO NOT run login inside the AI agent console (the browser window will be invisible). Please open a standard OS terminal and run 'login.bat' (Windows) or 'login.sh' (Mac/Linux) manually."
    ):
        self.message = message
        super().__init__(self.message)


class NotebookNotFoundError(NotebookLMError):
    """Raised when a specific notebook ID or name cannot be found."""

    pass


class CLIExecutionError(NotebookLMError):
    """Raised when the notebooklm CLI fails with a non-zero exit code."""

    pass


class CLITimeoutError(NotebookLMError):
    """Raised when the CLI execution exceeds the configured timeout."""

    pass
