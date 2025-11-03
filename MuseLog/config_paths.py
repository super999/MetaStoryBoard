from __future__ import annotations

import os
import sys
from functools import lru_cache


APP_SUBDIR = "MuseLog"


@lru_cache(maxsize=1)
def get_app_config_dir() -> str:
    """Return a per-user configuration directory shared across launches."""
    if os.name == "nt":
        # Use %APPDATA% for roaming profile, fall back to local app data or home.
        base = os.environ.get("APPDATA") or os.environ.get("LOCALAPPDATA")
        if not base:
            base = os.path.expanduser("~")
        return os.path.join(base, APP_SUBDIR)

    if sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
        return os.path.join(base, APP_SUBDIR)

    # Linux/Unix: follow XDG_CONFIG_HOME
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, APP_SUBDIR)


def ensure_config_dir() -> str:
    path = get_app_config_dir()
    os.makedirs(path, exist_ok=True)
    return path


def get_config_file(name: str) -> str:
    return os.path.join(ensure_config_dir(), name)
