from pathlib import Path


def get_steam_path() -> Path | None:
    """Safely resolve Steam installation path from steamclient.

    Returns:
        Path when Steam is detected, otherwise None.
    """
    try:
        from steamclient import STEAM_PATH
    except (ImportError, FileNotFoundError, OSError):
        return None

    if not STEAM_PATH:
        return None

    try:
        return Path(STEAM_PATH)
    except (TypeError, ValueError):
        return None


def get_steam_path_or_fallback(fallback: Path | None = None) -> Path:
    """Get Steam path or return a fallback path when unavailable."""
    steam_path = get_steam_path()
    if steam_path is not None:
        return steam_path

    if fallback is not None:
        return fallback

    return Path.home() / ".steam"
