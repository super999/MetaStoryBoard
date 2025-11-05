from __future__ import annotations

import json
from typing import Optional

from MuseLog.config_paths import get_config_file


class LastPathParams:
    def __init__(self, select_last_path: Optional[str] = None, enter_last_path: Optional[str] = None):
        self.select_last_path = select_last_path
        self.enter_last_path = enter_last_path


class PersistenceMixin:
    """State persistence helpers for explorer widget."""

    _config_filename = "tab_explorer.json"

    _cache_last_path_params: LastPathParams = LastPathParams()

    def _init_config_path(self) -> str:
        return get_config_file(self._config_filename)

    def _load_last_path_params(self) -> LastPathParams:
        try:
            with open(self._config_file, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except FileNotFoundError:
            return LastPathParams()
        except Exception:
            return LastPathParams()
        enter_path = data.get("enter_last_path") if isinstance(data, dict) else None
        select_path = data.get("select_last_path") if isinstance(data, dict) else None
        if not self._path_exists(select_path):
            select_path = None
        if not self._path_exists(enter_path):
            enter_path = None
        self._cache_last_path_params = LastPathParams(select_last_path=select_path, enter_last_path=enter_path)
        return self._cache_last_path_params

    def _save_selected_last_path(self, path: str) -> None:
        params = self._cache_last_path_params
        params.select_last_path = path
        self._save_last_path_params(params)

    def _save_enter_last_path(self, path: str) -> None:
        params = self._cache_last_path_params
        params.enter_last_path = path
        self._save_last_path_params(params)

    def _save_last_path_params(self, params: LastPathParams) -> None:
        if not params:
            return
        try:
            with open(self._config_file, "w", encoding="utf-8") as handle:
                json.dump(
                    {
                        "select_last_path": params.select_last_path,
                        "enter_last_path": params.enter_last_path,
                    },
                    handle, ensure_ascii=False, indent=2)
        except Exception:
            pass

    @staticmethod
    def _path_exists(path: Optional[str]) -> bool:
        import os
        if not path:
            return False
        return os.path.isdir(path)
