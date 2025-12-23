from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from bot.nlp_processor import NLPProcessor
from bot.extension_manager import ExtensionManager


class TelegramBotHandler:
    """
    Handles Telegram bot interactions and message processing.
    """

    def __init__(self, telegram_token: str, claude_api_key: str):
        self.telegram_token = telegram_token
        self.extension_manager = ExtensionManager()
        self.nlp_processor = NLPProcessor(claude_api_key, self.extension_manager)
        self.application = None

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command."""
        welcome_message = """
Welcome to the Extensible Bot! 🤖

I understand natural language commands and can help you with various tasks.

Available extensions:
"""
        for ext in self.extension_manager.get_all_extensions():
            welcome_message += f"\n• {ext.name}: {ext.description}"

        welcome_message += "\n\nJust send me a message with what you want to do!"

        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command."""
        help_message = """
How to use this bot:

1. Simply type what you want to do in natural language
2. I'll understand your intent and route it to the right extension
3. I'll extract the necessary parameters from your message
4. You'll get a response with the results

Examples:
• "What's the weather in New York?"
• "Search for information about Python programming"
• "Get me the latest news about AI"

Available extensions:
"""
        for ext in self.extension_manager.get_all_extensions():
            help_message += f"\n• {ext.name}: {ext.description}"

        await update.message.reply_text(help_message)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages."""
        user_message = update.message.text

        # Send "typing" action
        await update.message.chat.send_action("typing")

        try:
            # Process the command with NLP
            extension_name, parameters = await self.nlp_processor.process_command(user_message)

            if not extension_name:
                await update.message.reply_text(
                    "I couldn't understand your command. Please try rephrasing or use /help to see available commands."
                )
                return

            # Get the extension
            extension = self.extension_manager.get_extension(extension_name)

            if not extension:
                await update.message.reply_text(
                    f"Extension '{extension_name}' not found. Please use /help to see available extensions."
                )
                return

            # Validate parameters
            if not extension.validate_parameters(parameters):
                await update.message.reply_text(
                    "The parameters for this command are invalid. Please try again."
                )
                return

            # Execute the extension
            result = await extension.execute(parameters)

            # Send the result back to the user
            await update.message.reply_text(result)

        except Exception as e:
            error_message = f"An error occurred while processing your command: {str(e)}"
            await update.message.reply_text(error_message)
            print(f"Error handling message: {e}")

    def run(self):
        """Start the bot."""
        # Create the Application
        self.application = Application.builder().token(self.telegram_token).build()

        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Start the bot
        print("Bot is starting...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
