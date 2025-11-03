import logging
import os
import subprocess
import sys
from typing import Dict, List, Optional

from PySide6.QtCore import QModelIndex, QPoint, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QFileDialog,
    QListView,
    QMenu,
    QMessageBox,
    QStyle,
    QWidget,
)

from MuseLog.ui.ui_tab_favorites import Ui_TabFavorites
from MuseLog.favorites_store import FavoritesStore, FavoriteFolder


class TabFavoritesWidget(QWidget):
    """Simple favorites manager that keeps handy folders and their contents."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.ui = Ui_TabFavorites()
        self.ui.setupUi(self)

        self.ui.treeView.setHeaderHidden(True)
        self.ui.treeView.setUniformRowHeights(True)
        self.ui.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.listView.setEditTriggers(QListView.NoEditTriggers)
        self.ui.listView.setSelectionMode(QListView.ExtendedSelection)
        self.ui.listView.setUniformItemSizes(True)
        self.ui.listView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.lineFilter.setPlaceholderText("输入关键字以过滤右侧项目…")

        self._tree_model = QStandardItemModel(self.ui.treeView)
        self._tree_model.setHorizontalHeaderLabels(["收藏夹"])
        self.ui.treeView.setModel(self._tree_model)

        self._list_model = QStandardItemModel(self.ui.listView)
        self.ui.listView.setModel(self._list_model)

        self._store = FavoritesStore()
        self._favorites: List[FavoriteFolder] = []
        self._current_folder: Optional[str] = None
        self._current_entries: List[Dict[str, str]] = []
        self._filter_text: str = ""

        self._load_favorites()
        self._refresh_tree(select_first=True)

        self.ui.btnAddFolder.clicked.connect(self.on_add_folder)
        self.ui.btnRefresh.clicked.connect(self.on_refresh)
        self.ui.treeView.selectionModel().currentChanged.connect(self.on_tree_selection_changed)
        self.ui.treeView.doubleClicked.connect(self.on_tree_double_clicked)
        self.ui.treeView.customContextMenuRequested.connect(self.on_tree_context_menu)
        self.ui.listView.doubleClicked.connect(self.on_list_item_double_clicked)
        self.ui.listView.customContextMenuRequested.connect(self.on_list_context_menu)
        self.ui.lineFilter.textChanged.connect(self.on_filter_text_changed)

    def _load_favorites(self) -> None:
        try:
            self._favorites = self._store.load()
        except Exception as exc:
            logging.exception("读取收藏夹配置失败: %s", self._store.file_path)
            QMessageBox.warning(self, "加载失败", f"读取收藏夹配置时发生错误：\n{exc}")
            self._favorites = []

    # ------------------------------------------------------------------
    # UI 刷新
    # ------------------------------------------------------------------
    def _refresh_tree(self, *, select_first: bool = False) -> None:
        selected_path = self._current_folder
        self._tree_model.clear()
        self._tree_model.setHorizontalHeaderLabels(["收藏夹"])

        matched_index: Optional[QModelIndex] = None
        for entry in self._favorites:
            item = QStandardItem(entry.alias)
            item.setEditable(False)
            item.setData(entry.path, Qt.UserRole)
            item.setToolTip(entry.path)
            self._tree_model.appendRow(item)
            if selected_path and self._is_same_path(entry.path, selected_path):
                matched_index = item.index()

        if matched_index is not None:
            self.ui.treeView.setCurrentIndex(matched_index)
        elif select_first and self._tree_model.rowCount() > 0:
            index = self._tree_model.index(0, 0)
            self.ui.treeView.setCurrentIndex(index)
        else:
            self._current_folder = None
            self._current_entries.clear()
            self._apply_filter_to_list()

    def _apply_filter_to_list(self) -> None:
        self._list_model.clear()
        if not self._current_entries:
            return

        text = self._filter_text.lower()
        style = self.style()
        rows_added = 0

        for entry in self._current_entries:
            if text and text not in entry["name"].lower():
                continue
            item = QStandardItem(entry["name"])
            item.setEditable(False)
            icon = style.standardIcon(QStyle.SP_DirIcon if entry["is_dir"] else QStyle.SP_FileIcon)
            item.setIcon(icon)
            item.setData(entry["path"], Qt.UserRole)
            item.setToolTip(entry["path"])
            self._list_model.appendRow(item)
            rows_added += 1

        if rows_added == 0:
            placeholder = QStandardItem("(无匹配项目)")
            placeholder.setEnabled(False)
            self._list_model.appendRow(placeholder)

    # ------------------------------------------------------------------
    # 事件处理
    # ------------------------------------------------------------------
    def on_add_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "选择收藏文件夹")
        if not folder:
            return

        existing = next((fav for fav in self._favorites if self._is_same_path(fav.path, folder)), None)
        if existing:
            QMessageBox.information(self, "已存在", "该文件夹已在收藏列表中。")
            self._current_folder = existing.path
            self._load_folder_entries(existing.path)
            return

        favorite = self._store.add_folder(folder)
        self._favorites = self._store.load()
        self._current_folder = favorite.path
        self._refresh_tree()
        self._load_folder_entries(favorite.path)

    def on_refresh(self) -> None:
        self._load_favorites()
        self._refresh_tree(select_first=True)
        if self._current_folder:
            self._load_folder_entries(self._current_folder)

    def on_tree_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        path = current.data(Qt.UserRole)
        if not path:
            self._current_folder = None
            self._current_entries = []
            self._apply_filter_to_list()
            return

        self._current_folder = str(path)
        self._load_folder_entries(self._current_folder)

    def on_tree_double_clicked(self, index: QModelIndex) -> None:
        path = index.data(Qt.UserRole)
        if path:
            self._open_in_system(path)

    def on_tree_context_menu(self, point: QPoint) -> None:
        index = self.ui.treeView.indexAt(point)
        if not index.isValid():
            return

        path = index.data(Qt.UserRole)
        if not path:
            return

        menu = QMenu(self.ui.treeView)
        open_action = menu.addAction("打开")
        menu.addSeparator()
        remove_action = menu.addAction("移除收藏")
        action = menu.exec(self.ui.treeView.mapToGlobal(point))
        if action == open_action:
            self._open_in_system(path)
        elif action == remove_action:
            self._remove_favorite(path)

    def on_list_item_double_clicked(self, index: QModelIndex) -> None:
        path = index.data(Qt.UserRole)
        if path and os.path.exists(path):
            self._open_in_system(path)

    def on_list_context_menu(self, point: QPoint) -> None:
        index = self.ui.listView.indexAt(point)
        if not index.isValid():
            return

        path = index.data(Qt.UserRole)
        if not path or not os.path.exists(path):
            return

        menu = QMenu(self.ui.listView)
        open_action = menu.addAction("打开")
        reveal_action = menu.addAction("在资源管理器中显示")
        action = menu.exec(self.ui.listView.mapToGlobal(point))
        if action == open_action:
            self._open_in_system(path)
        elif action == reveal_action:
            self._reveal_in_explorer(path)

    def on_filter_text_changed(self, text: str) -> None:
        self._filter_text = text.strip()
        self._apply_filter_to_list()

    # ------------------------------------------------------------------
    # 数据与工具方法
    # ------------------------------------------------------------------
    def _load_folder_entries(self, folder: str) -> None:
        if not os.path.isdir(folder):
            QMessageBox.warning(self, "目录不存在", f"目录已不存在，将从收藏中移除：\n{folder}")
            self._remove_favorite(folder, silent=True)
            return

        entries: List[Dict[str, str]] = []
        try:
            with os.scandir(folder) as iterator:
                for entry in iterator:
                    entries.append(
                        {
                            "name": entry.name,
                            "path": entry.path,
                            "is_dir": entry.is_dir(),
                        }
                    )
        except PermissionError as exc:
            QMessageBox.warning(self, "无法访问", f"没有权限读取目录：\n{folder}\n{exc}")
            return
        except Exception as exc:
            logging.exception("读取收藏目录失败: %s", folder)
            QMessageBox.warning(self, "读取失败", f"读取目录时发生错误：\n{folder}\n{exc}")
            return

        self._current_entries = sorted(entries, key=lambda item: (not item["is_dir"], item["name"].lower()))
        self._apply_filter_to_list()

    def _remove_favorite(self, path: str, *, silent: bool = False) -> None:
        if self._current_folder and self._is_same_path(self._current_folder, path):
            self._current_folder = None
            self._current_entries.clear()
            self._apply_filter_to_list()

        try:
            changed = self._store.remove_folder(path)
        except Exception as exc:
            logging.exception("移除收藏失败: %s", path)
            QMessageBox.warning(self, "移除失败", f"写入收藏夹配置时发生错误：\n{exc}")
            return

        if not changed:
            return

        self._favorites = self._store.load()
        self._refresh_tree(select_first=True)
        if not silent:
            QMessageBox.information(self, "已移除", "收藏已移除。")

    @staticmethod
    def _normalize_path(path: Optional[str]) -> Optional[str]:
        if not path:
            return None
        return os.path.normcase(os.path.normpath(path))

    def _is_same_path(self, a: Optional[str], b: Optional[str]) -> bool:
        return self._normalize_path(a) == self._normalize_path(b)

    def _open_in_system(self, path: str) -> None:
        try:
            if os.name == "nt":
                os.startfile(path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.run(["open", path], check=False)
            else:
                subprocess.run(["xdg-open", path], check=False)
        except Exception as exc:
            logging.exception("打开路径失败: %s", path)
            QMessageBox.warning(self, "打开失败", f"无法打开：\n{path}\n{exc}")

    def _reveal_in_explorer(self, path: str) -> None:
        try:
            if os.name == "nt":
                if os.path.isdir(path):
                    os.startfile(path)  # type: ignore[attr-defined]
                else:
                    subprocess.run(["explorer", "/select,", path], check=False)
            elif sys.platform == "darwin":
                subprocess.run(["open", "-R", path], check=False)
            else:
                folder = path if os.path.isdir(path) else os.path.dirname(path)
                subprocess.run(["xdg-open", folder], check=False)
        except Exception as exc:
            logging.exception("定位路径失败: %s", path)
            QMessageBox.warning(self, "打开失败", f"无法定位到：\n{path}\n{exc}")
