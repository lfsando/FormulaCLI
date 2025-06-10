"""Utilities and lazy loading for the :mod:`formulacli` package."""

from __future__ import annotations

from typing import TYPE_CHECKING
import importlib

if TYPE_CHECKING:  # pragma: no cover - for type checkers only
    from .app import FormulaCLI


def __getattr__(name: str):
    """Lazily import ``FormulaCLI`` to avoid heavy dependencies at import time."""
    if name == "FormulaCLI":
        module = importlib.import_module(".app", __name__)
        return module.FormulaCLI
    raise AttributeError(f"module {__name__!r} has no attribute {name}")

