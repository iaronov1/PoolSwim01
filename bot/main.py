#!/usr/bin/env python3
"""
Main entry point for the Extensible Telegram Bot.
"""

import sys
from config.settings import settings
from bot.bot_handler import TelegramBotHandler


def main():
    """
    Initialize and start the Telegram bot.
    """
    print("=" * 50)
    print("Extensible Telegram Bot")
    print("=" * 50)

    try:
        # Validate settings
        settings.validate()
        print("✓ Configuration validated")

        # Create and start the bot
        bot = TelegramBotHandler(
            telegram_token=settings.TELEGRAM_BOT_TOKEN,
            claude_api_key=settings.CLAUDE_API_KEY
        )

        print("✓ Bot initialized")
        print("✓ Extensions loaded")
        print("\n🚀 Bot is running... Press Ctrl+C to stop.\n")

        # Run the bot
        bot.run()

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease make sure you have set the required environment variables:")
        print("  - TELEGRAM_BOT_TOKEN")
        print("  - CLAUDE_API_KEY")
        print("\nYou can set them in a .env file or as environment variables.")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
