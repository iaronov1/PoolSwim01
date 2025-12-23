# Extensible Telegram Bot Framework

A generic, extensible Telegram bot that uses natural language processing (powered by Claude AI) to understand commands and route them to appropriate extensions. Perfect for building intelligent bots that can handle complex tasks.

## Features

- **Natural Language Understanding**: Uses Claude AI to parse natural language commands and extract parameters
- **Extensible Plugin Architecture**: Easy-to-create extensions for any functionality
- **Automatic Command Routing**: Intelligent routing to the right extension based on user intent
- **Parameter Extraction**: Automatically extracts necessary parameters from natural language
- **Production Ready**: Includes Docker configuration and fly.io deployment setup
- **Sample Extension**: Wikipedia search extension demonstrating internet data fetching and transformation

## Architecture

```
┌─────────────────┐
│  Telegram User  │
└────────┬────────┘
         │
         │ Natural Language Command
         ▼
┌─────────────────────┐
│   Bot Handler       │
│  (Telegram API)     │
└─────────┬───────────┘
          │
          │ User Message
          ▼
┌─────────────────────┐
│   NLP Processor     │
│   (Claude AI)       │
└─────────┬───────────┘
          │
          │ Intent + Parameters
          ▼
┌─────────────────────┐
│  Extension Manager  │
└─────────┬───────────┘
          │
          │ Route to Extension
          ▼
┌─────────────────────┐
│   Extension         │
│ (WikipediaExtension)│
│   - Fetch Data      │
│   - Transform       │
│   - Return Result   │
└─────────┬───────────┘
          │
          │ Response
          ▼
┌─────────────────────┐
│  Telegram User      │
└─────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11 or higher
- A Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))
- Claude API Key (get from [Anthropic Console](https://console.anthropic.com/))

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd PoolSwim01
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your credentials:
   ```
   TELEGRAM_BOT_TOKEN=your_actual_bot_token
   CLAUDE_API_KEY=your_actual_claude_api_key
   ```

5. **Run the bot**
   ```bash
   python -m bot.main
   ```

6. **Test the bot**
   - Open Telegram and find your bot
   - Send `/start` to begin
   - Try natural language commands like:
     - "What is artificial intelligence?"
     - "Tell me about Python programming"
     - "Search for information about quantum computing"

## Creating Custom Extensions

Creating a new extension is simple! Here's a step-by-step guide:

### 1. Create a new Python file in the `extensions/` directory

```python
# extensions/my_extension.py

from typing import Dict, Any, List
from extensions.base_extension import BaseExtension

class MyExtension(BaseExtension):
    """
    Your extension description here.
    """

    def get_description(self) -> str:
        """Describe what your extension does."""
        return "Brief description of your extension's functionality"

    def get_keywords(self) -> List[str]:
        """Keywords that trigger your extension."""
        return ["keyword1", "keyword2", "trigger_phrase"]

    def get_parameter_schema(self) -> Dict[str, Any]:
        """Define expected parameters."""
        return {
            "param_name": {
                "type": "string",
                "description": "What this parameter represents",
                "required": True
            }
        }

    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate parameters before execution."""
        return "param_name" in parameters

    async def execute(self, parameters: Dict[str, Any]) -> str:
        """
        Main execution logic.

        This is where you:
        - Fetch data from APIs
        - Transform/process data
        - Perform calculations
        - Return formatted results
        """
        # Your logic here
        result = "Your processed result"
        return result
```

### 2. The extension will be automatically loaded

The `ExtensionManager` automatically discovers and loads all extensions from the `extensions/` directory. No registration needed!

### 3. Example: Weather Extension

```python
# extensions/weather_extension.py

from typing import Dict, Any, List
import aiohttp
from extensions.base_extension import BaseExtension

class WeatherExtension(BaseExtension):
    def get_description(self) -> str:
        return "Get current weather information for any city"

    def get_keywords(self) -> List[str]:
        return ["weather", "temperature", "forecast", "climate"]

    def get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "city": {
                "type": "string",
                "description": "City name",
                "required": True
            }
        }

    async def execute(self, parameters: Dict[str, Any]) -> str:
        city = parameters.get("city")

        # Fetch weather data from API
        weather_data = await self._fetch_weather(city)

        # Format and return result
        return f"Weather in {city}: {weather_data}"

    async def _fetch_weather(self, city: str) -> str:
        # Your API call here
        pass
```

## Deployment to fly.io

### Prerequisites
- Install [flyctl](https://fly.io/docs/hands-on/install-flyctl/)
- Create a fly.io account

### Deployment Steps

1. **Login to fly.io**
   ```bash
   flyctl auth login
   ```

2. **Create a new app**
   ```bash
   flyctl launch
   ```

   Follow the prompts:
   - Choose your app name
   - Select a region
   - Don't deploy yet (we need to set secrets first)

3. **Set environment secrets**
   ```bash
   flyctl secrets set TELEGRAM_BOT_TOKEN=your_token
   flyctl secrets set CLAUDE_API_KEY=your_api_key
   ```

4. **Deploy the bot**
   ```bash
   flyctl deploy
   ```

5. **Monitor logs**
   ```bash
   flyctl logs
   ```

### Updating Your Deployment

To update your bot after making changes:
```bash
flyctl deploy
```

## Project Structure

```
PoolSwim01/
├── bot/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── bot_handler.py       # Telegram bot logic
│   ├── nlp_processor.py     # Claude AI integration
│   └── extension_manager.py # Extension loader
├── extensions/
│   ├── __init__.py
│   ├── base_extension.py    # Base class for extensions
│   └── wikipedia_extension.py # Sample extension
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration management
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── fly.toml               # Fly.io configuration
├── .env.example          # Environment template
└── README.md            # This file
```

## How It Works

1. **User sends a message** in Telegram (e.g., "What is Python programming?")

2. **Bot receives the message** and sends it to the NLP Processor

3. **NLP Processor (Claude AI)** analyzes the message:
   - Identifies the intent (search for information)
   - Determines which extension to use (WikipediaExtension)
   - Extracts parameters (query: "Python programming")

4. **Extension Manager** routes the request to the correct extension

5. **Extension executes**:
   - Makes API calls (Wikipedia API)
   - Processes and transforms data
   - Returns formatted results

6. **Bot sends the response** back to the user in Telegram

## Advanced Features

### Adding Multiple Extensions

You can have multiple extensions working together:
- Weather extension
- News extension
- Calculator extension
- Translation extension
- Database query extension

The NLP processor will automatically route commands to the right extension based on context.

### Extension Communication

Extensions can be designed to work together by:
- Sharing data through the parameter system
- Creating composite extensions that call other extensions
- Building complex workflows

### Error Handling

The framework includes built-in error handling:
- Invalid parameters are caught and reported
- Extension failures are gracefully handled
- Users receive helpful error messages

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token from @BotFather | Yes |
| `CLAUDE_API_KEY` | Your Anthropic Claude API key | Yes |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No |
| `ENVIRONMENT` | Environment name (development, production) | No |

## Troubleshooting

### Bot doesn't respond
- Check that your `TELEGRAM_BOT_TOKEN` is correct
- Verify the bot is running (`python -m bot.main`)
- Check logs for errors

### NLP routing issues
- Verify your `CLAUDE_API_KEY` is valid
- Check that extensions have clear descriptions and keywords
- Review Claude API quotas/limits

### Extension not loading
- Ensure the extension file is in `extensions/` directory
- Check that the class inherits from `BaseExtension`
- Look for syntax errors in the extension code

## Contributing

To contribute:
1. Fork the repository
2. Create a new branch for your feature
3. Add your extension or improvement
4. Test thoroughly
5. Submit a pull request

## License

MIT License - feel free to use this framework for any purpose.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing extensions for examples
- Review the Claude AI documentation for NLP capabilities

## Future Enhancements

Potential improvements:
- Multi-language support
- Extension marketplace
- Web dashboard for monitoring
- Extension dependencies and versioning
- Caching layer for API calls
- User session management
- Permission system for extensions

---

Built with Python, Claude AI, and Telegram Bot API
