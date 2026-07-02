from __future__ import annotations

import secrets
from pathlib import Path


class ConsoleSecurityError(ValueError):
    """Raised when a console operation crosses a local safety boundary."""


ALLOWED_LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
SENSITIVE_PATH_MARKERS = {
    ".git",
    ".ssh",
    ".aws",
    ".azure",
    ".config",
    ".gnupg",
    "appdata",
    "browser profile",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "keychain",
    "login data",
    "raw_local_only_do_not_share",
    "token",
    "wallet",
}


def make_local_token() -> str:
    return secrets.token_urlsafe(24)


def assert_host_allowed(host: str, allow_lan: bool = False) -> None:
    normalized = (host or "").strip().lower()
    if normalized in ALLOWED_LOCAL_HOSTS:
        return
    if allow_lan and normalized not in {"", "*"}:
        return
    raise ConsoleSecurityError(
        "The local console binds to 127.0.0.1 by default. Use --allow-lan only "
        "when you explicitly understand the LAN exposure."
    )


def _contains_sensitive_marker(path: Path) -> bool:
    joined = " ".join(part.lower() for part in path.parts)
    return any(marker in joined for marker in SENSITIVE_PATH_MARKERS)


def safe_join(workspace: Path | str, *parts: str) -> Path:
    root = Path(workspace).expanduser().resolve()
    candidate = root.joinpath(*parts).expanduser().resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ConsoleSecurityError("Path traversal outside the console workspace is blocked.") from exc
    relative = candidate.relative_to(root)
    if _contains_sensitive_marker(relative):
        raise ConsoleSecurityError("Sensitive local-only paths are not readable through the console.")
    return candidate


def assert_path_within_workspace(workspace: Path | str, candidate: Path | str) -> Path:
    root = Path(workspace).expanduser().resolve()
    resolved = Path(candidate).expanduser().resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ConsoleSecurityError("Requested path is outside the configured console workspace.") from exc
    if _contains_sensitive_marker(resolved.relative_to(root)):
        raise ConsoleSecurityError("Sensitive local-only paths are not readable through the console.")
    return resolved


def validate_local_token(provided: str | None, expected: str) -> bool:
    if not provided or not secrets.compare_digest(provided, expected):
        raise ConsoleSecurityError("A valid local console token is required for this operation.")
    return True
