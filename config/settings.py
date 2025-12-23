import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """
    Application settings loaded from environment variables.
    """

    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    # Claude API Key for NLP processing
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

    # Optional: Additional settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

    @classmethod
    def validate(cls):
        """
        Validate that all required settings are present.
        """
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

        if not cls.CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY environment variable is required")

        return True


# Create a singleton instance
settings = Settings()
