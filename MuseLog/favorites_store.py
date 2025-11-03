from __future__ import annotations

import json
import os
from dataclasses import dataclass
from threading import Lock
from typing import ClassVar, List, Sequence

from MuseLog.config_paths import get_config_file


@dataclass(slots=True)
class FavoriteFolder:
    path: str
    alias: str

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "alias": self.alias}


class FavoritesStore:
    filename = "tab_favorites.json"

    _instance: ClassVar["FavoritesStore"] | None = None
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self.file_path = get_config_file(self.filename)
        self._initialized = True

    def load(self) -> List[FavoriteFolder]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as handle:
                raw = json.load(handle)
        except FileNotFoundError:
            return []
        except Exception:
            return []

        folders = raw.get("folders") if isinstance(raw, dict) else []
        results: List[FavoriteFolder] = []
        for entry in folders if isinstance(folders, Sequence) else []:
            if not isinstance(entry, dict):
                continue
            path = entry.get("path")
            alias = entry.get("alias")
            if not path or not isinstance(path, str):
                continue
            if not os.path.isdir(path):
                continue
            if not alias or not isinstance(alias, str):
                alias = self._derive_alias(path)
            results.append(FavoriteFolder(path=path, alias=alias))
        return sorted(results, key=lambda item: item.alias.lower())

    def save(self, folders: Sequence[FavoriteFolder]) -> None:
        try:
            with open(self.file_path, "w", encoding="utf-8") as handle:
                json.dump(
                    {"folders": [favorite.to_dict() for favorite in folders]},
                    handle,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception:
            pass

    def add_folder(self, path: str, alias: str | None = None) -> FavoriteFolder:
        folders = self.load()
        normalized_path = self._normalize(path)
        for favorite in folders:
            if self._normalize(favorite.path) == normalized_path:
                return favorite

        alias = alias or self._derive_alias(path)
        alias = self._ensure_unique_alias(alias, folders)
        favorite = FavoriteFolder(path=path, alias=alias)
        folders.append(favorite)
        folders.sort(key=lambda item: item.alias.lower())
        self.save(folders)
        return favorite

    def remove_folder(self, path: str) -> bool:
        folders = self.load()
        normalized_path = self._normalize(path)
        filtered = [favorite for favorite in folders if self._normalize(favorite.path) != normalized_path]
        if len(filtered) == len(folders):
            return False
        self.save(filtered)
        return True

    @staticmethod
    def _derive_alias(path: str) -> str:
        cleaned = os.path.normpath(path)
        name = os.path.basename(cleaned)
        return name or cleaned

    @staticmethod
    def _normalize(path: str) -> str:
        return os.path.normcase(os.path.normpath(path))

    def _ensure_unique_alias(self, alias: str, folders: Sequence[FavoriteFolder]) -> str:
        existing = {item.alias.lower() for item in folders}
        candidate = alias
        counter = 2
        while candidate.lower() in existing:
            candidate = f"{alias} ({counter})"
            counter += 1
        return candidate


def get_favorites_store() -> FavoritesStore:
    """Return the shared FavoritesStore instance."""
    return FavoritesStore()


def list_favorites() -> List[FavoriteFolder]:
    """List all favorite folders using the shared store."""
    return get_favorites_store().load()


def add_favorite_folder(path: str, alias: str | None = None) -> FavoriteFolder:
    """Add a folder to favorites via the shared store."""
    return get_favorites_store().add_folder(path, alias)


def remove_favorite_folder(path: str) -> bool:
    """Remove a folder from favorites via the shared store."""
    return get_favorites_store().remove_folder(path)
