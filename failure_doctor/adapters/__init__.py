"""Public-safe automation adapter entrypoints."""

from .core import diagnose_adapter_input, normalize_adapter_input

__all__ = ["diagnose_adapter_input", "normalize_adapter_input"]
