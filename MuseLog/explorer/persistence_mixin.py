from __future__ import annotations

import json
from typing import Optional

from MuseLog.config_paths import get_config_file


class PersistenceMixin:
    """State persistence helpers for explorer widget."""

    _config_filename = "tab_explorer.json"

    def _init_config_path(self) -> str:
        return get_config_file(self._config_filename)

    def _load_last_path(self) -> Optional[str]:
        try:
            with open(self._config_file, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except FileNotFoundError:
            return None
        except Exception:
            return None
        path = data.get("last_path") if isinstance(data, dict) else None
        if not path or not isinstance(path, str):
            return None
        if not self._path_exists(path):
            return None
        return path

    def _save_last_path(self, path: str) -> None:
        if not path:
            return
        try:
            with open(self._config_file, "w", encoding="utf-8") as handle:
                json.dump({"last_path": path}, handle, ensure_ascii=False, indent=2)
        except Exception:
            pass

    @staticmethod
    def _path_exists(path: Optional[str]) -> bool:
        import os

        if not path:
            return False
        return os.path.isdir(path)
