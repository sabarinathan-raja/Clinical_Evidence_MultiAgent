"""Core application infrastructure."""

from backend.core.config import settings, get_settings
from backend.core.model_gateway import (
    model_gateway,
    get_model_gateway
)

__all__ = [
    "settings",
    "get_settings",
    "model_gateway",
    "get_model_gateway"
]