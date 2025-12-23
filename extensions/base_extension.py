from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class BaseExtension(ABC):
    """
    Base class for all bot extensions.

    Extensions should inherit from this class and implement the required methods.
    """

    def __init__(self):
        self.name = self.__class__.__name__
        self.description = self.get_description()
        self.keywords = self.get_keywords()

    @abstractmethod
    def get_description(self) -> str:
        """
        Return a description of what this extension does.
        This is used by the NLP processor to route commands.
        """
        pass

    @abstractmethod
    def get_keywords(self) -> List[str]:
        """
        Return a list of keywords that might trigger this extension.
        These help the NLP processor identify the right extension.
        """
        pass

    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> str:
        """
        Execute the extension's main functionality.

        Args:
            parameters: Dictionary of extracted parameters from the natural language command

        Returns:
            Response string to send back to the user
        """
        pass

    def get_parameter_schema(self) -> Dict[str, Any]:
        """
        Optional: Define the expected parameter schema for this extension.
        This helps the NLP processor extract the right parameters.

        Returns:
            Dictionary describing expected parameters
        """
        return {}

    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Optional: Validate that the provided parameters are correct.

        Args:
            parameters: Dictionary of parameters to validate

        Returns:
            True if valid, False otherwise
        """
        return True
