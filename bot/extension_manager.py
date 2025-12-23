import os
import importlib
import inspect
from typing import List, Dict, Optional
from extensions.base_extension import BaseExtension


class ExtensionManager:
    """
    Manages loading and accessing bot extensions.
    """

    def __init__(self):
        self.extensions: Dict[str, BaseExtension] = {}
        self.load_extensions()

    def load_extensions(self):
        """
        Dynamically load all extensions from the extensions directory.
        """
        extensions_dir = "extensions"

        # Get all Python files in extensions directory
        for filename in os.listdir(extensions_dir):
            if filename.endswith(".py") and not filename.startswith("_") and filename != "base_extension.py":
                module_name = filename[:-3]

                try:
                    # Import the module
                    module = importlib.import_module(f"extensions.{module_name}")

                    # Find all classes that inherit from BaseExtension
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseExtension) and obj != BaseExtension:
                            # Instantiate the extension
                            extension_instance = obj()
                            self.extensions[extension_instance.name] = extension_instance
                            print(f"Loaded extension: {extension_instance.name}")

                except Exception as e:
                    print(f"Error loading extension {module_name}: {e}")

    def get_extension(self, name: str) -> Optional[BaseExtension]:
        """
        Get an extension by name.

        Args:
            name: Name of the extension

        Returns:
            Extension instance or None if not found
        """
        return self.extensions.get(name)

    def get_all_extensions(self) -> List[BaseExtension]:
        """
        Get all loaded extensions.

        Returns:
            List of all extension instances
        """
        return list(self.extensions.values())

    def get_extension_info(self) -> List[Dict[str, str]]:
        """
        Get information about all extensions for the NLP processor.

        Returns:
            List of dictionaries containing extension information
        """
        info = []
        for ext in self.extensions.values():
            info.append({
                "name": ext.name,
                "description": ext.description,
                "keywords": ", ".join(ext.keywords),
                "parameters": str(ext.get_parameter_schema())
            })
        return info
