import json
from typing import Dict, Any, Tuple, Optional
from anthropic import AsyncAnthropic
from bot.extension_manager import ExtensionManager


class NLPProcessor:
    """
    Processes natural language commands using Claude AI to identify intent
    and extract parameters for routing to extensions.
    """

    def __init__(self, api_key: str, extension_manager: ExtensionManager):
        self.client = AsyncAnthropic(api_key=api_key)
        self.extension_manager = extension_manager

    async def process_command(self, user_message: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Process a natural language command to identify the target extension and extract parameters.

        Args:
            user_message: The user's natural language command

        Returns:
            Tuple of (extension_name, parameters_dict)
        """
        # Get information about available extensions
        extensions_info = self.extension_manager.get_extension_info()

        # Create the prompt for Claude
        prompt = self._create_routing_prompt(user_message, extensions_info)

        try:
            # Call Claude API (async)
            message = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse the response
            response_text = message.content[0].text
            result = json.loads(response_text)

            extension_name = result.get("extension")
            parameters = result.get("parameters", {})

            return extension_name, parameters

        except Exception as e:
            print(f"Error processing command with Claude: {e}")
            return None, {}

    def _create_routing_prompt(self, user_message: str, extensions_info: list) -> str:
        """
        Create the prompt for Claude to analyze the command.

        Args:
            user_message: The user's message
            extensions_info: Information about available extensions

        Returns:
            Formatted prompt string
        """
        extensions_desc = "\n".join([
            f"- {ext['name']}: {ext['description']} (Keywords: {ext['keywords']})"
            for ext in extensions_info
        ])

        prompt = f"""You are a command routing system for a Telegram bot. Your job is to analyze a user's natural language command and determine:
1. Which extension should handle this command
2. What parameters should be extracted from the command

Available extensions:
{extensions_desc}

User command: "{user_message}"

Analyze the command and respond with a JSON object in this exact format:
{{
    "extension": "ExtensionClassName",
    "parameters": {{
        "param1": "value1",
        "param2": "value2"
    }}
}}

If no extension matches the command, return:
{{
    "extension": null,
    "parameters": {{}}
}}

Important:
- The extension name must match exactly one of the available extensions listed above
- Extract all relevant parameters from the user's message
- Be smart about understanding intent even if keywords don't match exactly
- Return ONLY the JSON object, no other text
"""
        return prompt
