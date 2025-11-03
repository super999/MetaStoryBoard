from __future__ import annotations

import os
from typing import List, Optional

from PySide6.QtCore import QDir, QModelIndex
from PySide6.QtWidgets import QMessageBox


class NavigationMixin:
    """Navigation, history, and tree handling."""

    _history_limit = 50

    def _init_navigation_state(self) -> None:
        self._history: List[str] = []
        self._current_path: Optional[str] = None
        self._suppress_tree_selection: bool = False

    # Public slots ---------------------------------------------------------
    def on_enter_clicked(self) -> None:
        path = self.ui.lineAddress.text().strip()
        self.navigate_to_path(path)

    def navigate_to_path(self, path: str, *, add_history: bool = True, update_tree: bool = True) -> None:
        if not path:
            return
        path = os.path.normpath(path)
        if os.path.isfile(path):
            path = os.path.dirname(path)
        if not os.path.isdir(path):
            QMessageBox.warning(self, "无效路径", f"目录不存在：\n{path}", QMessageBox.Ok)
            return

        self.ui.lineAddress.setText(path)
        model_index = self.model.index(path)
        if not model_index.isValid():
            model_index = self.model.setRootPath(path)
        if update_tree:
            self._suppress_tree_selection = True
            try:
                self.ui.treeView.setRootIndex(model_index)
                self.ui.treeView.setCurrentIndex(model_index)
            finally:
                self._suppress_tree_selection = False
        self.show_directory_metadata(path)
        self._save_last_path(path)
        self._set_current_path(path, add_history=add_history)

    def on_tree_selection_changed(self, selected, _deselected) -> None:
        if self._suppress_tree_selection:
            return
        indexes: List[QModelIndex] = selected.indexes()
        if not indexes:
            return
        idx = indexes[0]
        path = self.model.filePath(idx)
        if os.path.isfile(path):
            path = os.path.dirname(path)
        if not os.path.isdir(path):
            return
        self.ui.lineAddress.setText(path)
        self.show_directory_metadata(path)
        self._set_current_path(path, add_history=True)
        self._save_last_path(path)

    def on_back_clicked(self) -> None:
        if not self._history:
            return
        target_path: Optional[str] = None
        while self._history and not target_path:
            candidate = self._history.pop()
            if candidate and os.path.isdir(candidate):
                target_path = candidate
        if target_path:
            self.navigate_to_path(target_path, add_history=False)
        else:
            QMessageBox.information(self, "历史为空", "没有可返回的目录。", QMessageBox.Ok)
        self._update_nav_buttons()

    def on_go_up_clicked(self) -> None:
        current_path = self._current_path or self.ui.lineAddress.text().strip()
        if not current_path:
            return
        if not os.path.isdir(current_path):
            current_path = os.path.dirname(current_path)
        dir_obj = QDir(current_path)
        if not dir_obj.exists():
            parent_path = self._find_existing_parent(current_path)
            if not parent_path:
                return
            dir_obj = QDir(parent_path)
        if not dir_obj.cdUp():
            return
        parent = os.path.normpath(dir_obj.absolutePath())
        self.navigate_to_path(parent)

    def on_refresh_clicked(self) -> None:
        current_path = self._current_path or self.ui.lineAddress.text().strip()
        if not current_path or not os.path.isdir(current_path):
            return
        try:
            index = self.model.index(current_path)
            if hasattr(self.model, "refresh"):
                if index.isValid():
                    self.model.refresh(index)
                else:
                    self.model.refresh()
        except Exception:
            pass
        self.navigate_to_path(current_path, add_history=False, update_tree=True)

    # Internal helpers ----------------------------------------------------
    def _set_current_path(self, path: str, *, add_history: bool = True) -> None:
        if not path:
            return
        normalized_new = self._normalize_path(path)
        normalized_current = self._normalize_path(self._current_path)
        if add_history and self._current_path and normalized_new != normalized_current:
            if not self._history or self._normalize_path(self._history[-1]) != normalized_current:
                self._history.append(self._current_path)
                self._trim_history()
        self._current_path = path
        self._update_nav_buttons()

    def _normalize_path(self, path: Optional[str]) -> Optional[str]:
        if not path:
            return None
        return os.path.normcase(os.path.normpath(path))

    def _trim_history(self) -> None:
        overflow = len(self._history) - self._history_limit
        if overflow > 0:
            del self._history[0:overflow]

    def _find_existing_parent(self, path: str) -> Optional[str]:
        candidate = os.path.normpath(path)
        visited = set()
        while True:
            normalized_candidate = self._normalize_path(candidate)
            if normalized_candidate in visited:
                return None
            visited.add(normalized_candidate)
            if os.path.isdir(candidate):
                return candidate
            parent = os.path.dirname(candidate)
            if not parent or self._normalize_path(parent) == normalized_candidate:
                return None
            candidate = parent

    def _update_nav_buttons(self) -> None:
        self.ui.btnBack.setEnabled(bool(self._history))
        current = self._current_path
        current_exists = bool(current and os.path.isdir(current))
        can_go_up = False
        if current_exists:
            dir_obj = QDir(current)
            can_go_up = dir_obj.cdUp()
        self.ui.btnGoUp.setEnabled(can_go_up)
        self.ui.btnRefresh.setEnabled(current_exists)
