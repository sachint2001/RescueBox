import logging
from abc import ABC, abstractmethod
from typing import Any, Dict


class AbstractInputsParser(ABC):
    """
    Abstract base class for all input parsers.
    """

    logger = logging.getLogger(__name__)  # Class-level logger for consistent logging

    def __init__(self, name: str):
        self.name = name
        self.validator_type: Any = None  # Child classes must define this

    @property
    @abstractmethod
    def schema_function(self) -> Dict[str, Any]:
        """Child classes must define a schema function dictionary."""
        raise NotImplementedError("Subclasses must implement `schema_function`")

    @abstractmethod
    def params_parser(self, params: str):
        """
        Parses CLI parameters dynamically using `self.schema_function`.
        """
        raise NotImplementedError("Subclasses must implement `params_parser`")

    @abstractmethod
    def validate_inputs(self, inputs: dict):
        """Validate input data."""
        raise NotImplementedError("Subclasses must implement `validate_inputs`")

    @abstractmethod
    def cli_parser(self, path: str):
        """Parse CLI input."""
        raise NotImplementedError("Subclasses must implement `cli_parser`")
