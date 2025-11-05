from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

from MuseLog.config_paths import get_config_file


class LastPathParams:
    def __init__(self, select_last_path: Optional[str] = None, enter_last_path: Optional[str] = None):
        self.select_last_path = select_last_path
        self.enter_last_path = enter_last_path


class PersistenceMixin:
    """State persistence helpers for explorer widget with multi-tab support."""

    _config_filename = "tab_explorer.json"

    _config_data: Optional[Dict[str, object]] = None

    def _init_config_path(self) -> str:
        return get_config_file(self._config_filename)

    # ------------------------------------------------------------------
    # Config management (class-level)
    # ------------------------------------------------------------------
    @classmethod
    def _get_config_path(cls) -> str:
        return get_config_file(cls._config_filename)

    @classmethod
    def _load_config(cls) -> Dict[str, object]:
        if cls._config_data is not None:
            return cls._config_data

        try:
            with open(cls._get_config_path(), "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except FileNotFoundError:
            data = {}
        except Exception:
            data = {}

        if not isinstance(data, dict):
            data = {}

        if "tabs" not in data:
            enter_path = data.get("enter_last_path") if isinstance(data, dict) else None
            select_path = data.get("select_last_path") if isinstance(data, dict) else None
            tabs: List[Dict[str, Optional[str]]] = []
            if enter_path or select_path:
                tabs.append(cls._build_tab_entry("explorer-1", enter_path, select_path))
            data = {
                "tabs": tabs,
                "next_id": cls._infer_next_id(tabs),
            }
        else:
            raw_tabs = data.get("tabs", [])
            tabs: List[Dict[str, Optional[str]]] = []
            if isinstance(raw_tabs, list):
                for item in raw_tabs:
                    if not isinstance(item, dict):
                        continue
                    tab_id = str(item.get("tab_id") or "").strip()
                    if not tab_id:
                        continue
                    enter = item.get("enter_last_path")
                    select = item.get("select_last_path")
                    tabs.append(cls._build_tab_entry(tab_id, enter, select))
            data["tabs"] = tabs
            next_id = data.get("next_id")
            if not isinstance(next_id, int) or next_id < 1:
                data["next_id"] = cls._infer_next_id(tabs)

        cls._config_data = data
        return data

    @classmethod
    def _save_config(cls, data: Dict[str, object]) -> None:
        cls._config_data = data
        try:
            os.makedirs(os.path.dirname(cls._get_config_path()), exist_ok=True)
            with open(cls._get_config_path(), "w", encoding="utf-8") as handle:
                json.dump(data, handle, ensure_ascii=False, indent=2)
        except Exception:
            pass

    @classmethod
    def _build_tab_entry(
        cls,
        tab_id: str,
        enter_path: Optional[str],
        select_path: Optional[str],
    ) -> Dict[str, Optional[str]]:
        return {
            "tab_id": tab_id,
            "enter_last_path": cls._normalize_path_string(enter_path),
            "select_last_path": cls._normalize_path_string(select_path),
        }

    @staticmethod
    def _normalize_path_string(path: Optional[str]) -> Optional[str]:
        if not path or not isinstance(path, str):
            return None
        stripped = path.strip()
        if not stripped:
            return None
        return os.path.normpath(stripped)

    @classmethod
    def _infer_next_id(cls, tabs: List[Dict[str, Optional[str]]]) -> int:
        max_id = 0
        for tab in tabs:
            tab_id = str(tab.get("tab_id") or "")
            if tab_id.startswith("explorer-"):
                suffix = tab_id.split("-", 1)[-1]
                try:
                    value = int(suffix)
                except ValueError:
                    continue
                max_id = max(max_id, value)
        return max_id + 1 if max_id > 0 else 1

    @classmethod
    def allocate_tab_id(cls) -> str:
        data = cls._load_config()
        next_id = data.get("next_id")
        if not isinstance(next_id, int) or next_id < 1:
            next_id = cls._infer_next_id(data.get("tabs", []))
        tabs: List[Dict[str, Optional[str]]] = data.get("tabs", [])  # type: ignore[assignment]
        existing_ids = {str(entry.get("tab_id")) for entry in tabs if isinstance(entry, dict)}
        tab_id = f"explorer-{next_id}"
        while tab_id in existing_ids:
            next_id += 1
            tab_id = f"explorer-{next_id}"
        new_entry = cls._build_tab_entry(tab_id, None, None)
        tabs.append(new_entry)
        data["tabs"] = tabs
        data["next_id"] = next_id + 1
        cls._save_config(data)
        return tab_id

    @classmethod
    def get_saved_tabs(cls) -> List[Dict[str, Optional[str]]]:
        data = cls._load_config()
        tabs = data.get("tabs", [])
        if not isinstance(tabs, list):
            return []
        result: List[Dict[str, Optional[str]]] = []
        for tab in tabs:
            if isinstance(tab, dict):
                result.append(dict(tab))
        return result

    @classmethod
    def remove_tab_state(cls, tab_id: str) -> None:
        data = cls._load_config()
        tabs = data.get("tabs", [])
        if not isinstance(tabs, list):
            return
        new_tabs = [tab for tab in tabs if isinstance(tab, dict) and tab.get("tab_id") != tab_id]
        if len(new_tabs) == len(tabs):
            return
        data["tabs"] = new_tabs
        cls._save_config(data)

    # ------------------------------------------------------------------
    # Instance helpers
    # ------------------------------------------------------------------
    def _load_last_path_params(
        self,
        tab_id: str,
        *,
        default_enter_path: Optional[str] = None,
        default_select_path: Optional[str] = None,
    ) -> LastPathParams:
        data = self._load_config()
        tabs = data.get("tabs", [])
        if not isinstance(tabs, list):
            tabs = []

        entry = None
        for candidate in tabs:
            if isinstance(candidate, dict) and candidate.get("tab_id") == tab_id:
                entry = candidate
                break

        if entry is None:
            entry = self._build_tab_entry(tab_id, default_enter_path, default_select_path)
            tabs.append(entry)
            data["tabs"] = tabs
            self._save_config(data)
        else:
            updated = False
            if default_enter_path and self._path_exists(default_enter_path):
                if entry.get("enter_last_path") != default_enter_path:
                    entry["enter_last_path"] = default_enter_path
                    updated = True
            if default_select_path and self._path_exists(default_select_path):
                if entry.get("select_last_path") != default_select_path:
                    entry["select_last_path"] = default_select_path
                    updated = True
            if updated:
                self._save_config(data)

        enter_path = entry.get("enter_last_path") if isinstance(entry, dict) else None
        select_path = entry.get("select_last_path") if isinstance(entry, dict) else None
        if not self._path_exists(enter_path):
            enter_path = None
        if not self._path_exists(select_path):
            select_path = None

        params = LastPathParams(select_last_path=select_path, enter_last_path=enter_path)
        self._cache_last_path_params = params
        self._tab_id = tab_id
        return params

    def _save_selected_last_path(self, path: str) -> None:
        params = getattr(self, "_cache_last_path_params", LastPathParams())
        params.select_last_path = path
        self._cache_last_path_params = params
        self._save_last_path_params(params)

    def _save_enter_last_path(self, path: str) -> None:
        params = getattr(self, "_cache_last_path_params", LastPathParams())
        params.enter_last_path = path
        self._cache_last_path_params = params
        self._save_last_path_params(params)

    def _save_last_path_params(self, params: LastPathParams) -> None:
        tab_id = getattr(self, "_tab_id", None)
        if not tab_id:
            return

        data = self._load_config()
        tabs = data.get("tabs", [])
        if not isinstance(tabs, list):
            return
        for entry in tabs:
            if not isinstance(entry, dict):
                continue
            if entry.get("tab_id") != tab_id:
                continue
            entry["enter_last_path"] = params.enter_last_path
            entry["select_last_path"] = params.select_last_path
            self._save_config(data)
            break

    @staticmethod
    def _path_exists(path: Optional[str]) -> bool:
        if not path:
            return False
        return os.path.isdir(path)
