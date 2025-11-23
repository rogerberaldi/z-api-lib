"""Utility functions and classes for zapi_async."""

from __future__ import annotations
import logging
from typing import TypeVar, Any


__version__ = "0.1.0"
__author__ = "Z-API Async Contributors"
__license__ = "MIT"


class Version:
    """Version information."""
    
    def __init__(self, version: str):
        self.version = version
        parts = version.split(".")
        self.major = int(parts[0]) if len(parts) > 0 else 0
        self.minor = int(parts[1]) if len(parts) > 1 else 0
        self.patch = int(parts[2]) if len(parts) > 2 else 0
    
    def __str__(self) -> str:
        return self.version
    
    def __repr__(self) -> str:
        return f"Version('{self.version}')"


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure logging for zapi_async.
    
    Args:
        level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


T = TypeVar('T')


def ensure_list(value: T | list[T]) -> list[T]:
    """
    Ensure value is a list.
    
    Args:
        value: Single value or list
        
    Returns:
        List containing the value(s)
    """
    if isinstance(value, list):
        return value
    return [value]


def remove_none_values(data: dict[str, Any]) -> dict[str, Any]:
    """
    Remove None values from dictionary.
    
    Args:
        data: Dictionary to clean
        
    Returns:
        Dictionary without None values
    """
    return {k: v for k, v in data.items() if v is not None}
