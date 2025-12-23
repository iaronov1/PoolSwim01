from typing import Dict, Any, List
import aiohttp
from extensions.base_extension import BaseExtension


class WikipediaExtension(BaseExtension):
    """
    Extension for searching and retrieving Wikipedia articles.
    Demonstrates fetching data from the internet, transforming it, and returning results.
    """

    def get_description(self) -> str:
        return "Search Wikipedia for information about any topic and get a summary"

    def get_keywords(self) -> List[str]:
        return ["wikipedia", "wiki", "search", "information", "what is", "who is", "tell me about", "look up"]

    def get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "query": {
                "type": "string",
                "description": "The search query or topic to look up on Wikipedia",
                "required": True
            }
        }

    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate that we have a query parameter."""
        return "query" in parameters and isinstance(parameters["query"], str) and len(parameters["query"]) > 0

    async def execute(self, parameters: Dict[str, Any]) -> str:
        """
        Search Wikipedia and return a summary.

        Args:
            parameters: Must contain 'query' key with the search term

        Returns:
            Formatted Wikipedia summary or error message
        """
        query = parameters.get("query", "")

        if not query:
            return "Please provide a search query."

        try:
            # Search Wikipedia
            summary = await self._search_wikipedia(query)

            if summary:
                return f"📚 Wikipedia Summary for '{query}':\n\n{summary}"
            else:
                return f"No Wikipedia article found for '{query}'. Please try a different search term."

        except Exception as e:
            return f"Error searching Wikipedia: {str(e)}"

    async def _search_wikipedia(self, query: str) -> str:
        """
        Search Wikipedia API and return a summary.

        Args:
            query: Search term

        Returns:
            Article summary or empty string if not found
        """
        # Wikipedia API endpoint
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "_")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Extract the summary
                        title = data.get("title", "")
                        extract = data.get("extract", "")
                        page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")

                        if extract:
                            # Limit summary length
                            max_length = 800
                            if len(extract) > max_length:
                                extract = extract[:max_length] + "..."

                            result = f"{extract}\n\n🔗 Read more: {page_url}"
                            return result

                    elif response.status == 404:
                        # Try a search instead
                        return await self._wikipedia_search_fallback(query, session)

                    return ""

            except Exception as e:
                print(f"Error fetching Wikipedia data: {e}")
                return ""

    async def _wikipedia_search_fallback(self, query: str, session: aiohttp.ClientSession) -> str:
        """
        Fallback: Use Wikipedia search API to find articles.

        Args:
            query: Search term
            session: aiohttp session

        Returns:
            Summary of the first search result or empty string
        """
        search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={query}&limit=1&format=json"

        try:
            async with session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()

                    if len(data) >= 4 and len(data[1]) > 0:
                        # Get the first result
                        title = data[1][0]
                        description = data[2][0] if len(data[2]) > 0 else ""
                        url = data[3][0] if len(data[3]) > 0 else ""

                        if description:
                            return f"{description}\n\n🔗 Read more: {url}"

        except Exception as e:
            print(f"Error in Wikipedia search fallback: {e}")

        return ""
