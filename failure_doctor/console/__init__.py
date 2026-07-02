"""Local web console for Agent Failure Doctor.

The console is intentionally local-first: it binds to loopback by default,
serves bundled assets only, and treats raw evidence as non-shareable unless a
sanitized pack is explicitly provided.
"""

from __future__ import annotations

__all__ = ["__version__"]

__version__ = "3.7.0"
