import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Config:
    NOTEBOOKLM_CLI = os.getenv("NOTEBOOKLM_CLI", "notebooklm")

    try:
        NOTEBOOKLM_TIMEOUT = int(os.getenv("NOTEBOOKLM_TIMEOUT", "180"))
    except ValueError:
        NOTEBOOKLM_TIMEOUT = 180

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE = os.getenv("LOG_FILE", "logs/notebooklm-mcp.log")

    @classmethod
    def get_summary(cls):
        return {
            "NOTEBOOKLM_CLI": cls.NOTEBOOKLM_CLI,
            "NOTEBOOKLM_TIMEOUT": cls.NOTEBOOKLM_TIMEOUT,
            "LOG_LEVEL": cls.LOG_LEVEL,
            "LOG_FILE": cls.LOG_FILE,
        }


config = Config()
