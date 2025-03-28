import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class AbstractParser(ABC):
    """
    Abstract base class for all parsers.
    Each parser must define:
    - Input validation
    - CLI parsing
    - API routes (automatically registered)
    """

    def __init__(self, name: str, version: str = "1.0.0", author: str = "Unknown", description: str = ""):
        self.name = name
        self.version = version
        self.author = author
        self.description = description

    @abstractmethod
    def cli_parser(self, path: str):
        """Parse CLI input."""
        pass

    @abstractmethod
    def validate_inputs(self, inputs: Dict[str, Any]):
        """Validate input data."""
        pass

    @property
    @abstractmethod
    def routes(self) -> List[Dict[str, Any]]:
        """
        Define API routes for this parser.
        Every parser **must define** its own routes.
        """
        pass

    @property
    @abstractmethod
    def task_schema(self) -> Dict[str, Any]:
        """
        Return a schema dict (used by RescueBox desktop UI).
        This replaces the `@app.command('task_schema')` handler in the plugin.
        """
        pass

    @property
    def metadata(self) -> Dict[str, Any]:
        """Returns the metadata of the parser (configurable)."""
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
        }
