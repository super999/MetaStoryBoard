import logging
import os
import subprocess
import sys
from typing import Dict, List, Optional

from PySide6.QtCore import QModelIndex, QPoint, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QListView,
    QMenu,
    QMessageBox,
    QStyle,
    QWidget,QDialog
)

from MuseLog.favorites_store import FavoriteNode, FavoritesStore
from MuseLog.ui.ui_tab_favorites import Ui_TabFavorites
from MuseLog.favorites_new_folder_dialog import DialogFavoritesNewFolder


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
        self._root: FavoriteNode = self._store.get_root()
        self._node_index: Dict[int, FavoriteNode] = {}
        self._item_index: Dict[int, QStandardItem] = {}
        self._current_node_id: int = self._root.node_id
        self._current_children: List[FavoriteNode] = []
        self._filter_text: str = ""

        self._reload_from_store()
        self._refresh_tree()

        self.ui.btnAddFolder.clicked.connect(self.on_add_folder)
        self.ui.btnRefresh.clicked.connect(self.on_refresh)
        self.ui.treeView.selectionModel().currentChanged.connect(self.on_tree_selection_changed)
        self.ui.treeView.doubleClicked.connect(self.on_tree_double_clicked)
        self.ui.treeView.customContextMenuRequested.connect(self.on_tree_context_menu)
        self.ui.listView.doubleClicked.connect(self.on_list_item_double_clicked)
        self.ui.listView.customContextMenuRequested.connect(self.on_list_context_menu)
        self.ui.lineFilter.textChanged.connect(self.on_filter_text_changed)

    def _reload_from_store(self) -> None:
        try:
            self._root = self._store.get_root()
        except Exception as exc:
            logging.exception("读取收藏夹配置失败: %s", self._store.file_path)
            QMessageBox.warning(self, "加载失败", f"读取收藏夹配置时发生错误：\n{exc}")
            self._root = FavoriteNode(0, "收藏夹", "", 0.0)
        self._rebuild_node_index()
        if self._current_node_id not in self._node_index:
            self._current_node_id = self._root.node_id

    def _rebuild_node_index(self) -> None:
        self._node_index = {}

        def walk(node: FavoriteNode) -> None:
            self._node_index[node.node_id] = node
            for child in node.children:
                walk(child)

        walk(self._root)

    # ------------------------------------------------------------------
    # UI 刷新
    # ------------------------------------------------------------------
    def _refresh_tree(self) -> None:
        target_node_id = self._current_node_id if self._current_node_id in self._node_index else self._root.node_id
        self._tree_model.clear()
        self._tree_model.setHorizontalHeaderLabels(["收藏夹"])
        self._item_index = {}

        self._build_tree_items(self._root, None)
        self.ui.treeView.expandAll()

        target_item = self._item_index.get(target_node_id) or self._item_index.get(self._root.node_id)
        if target_item is not None:
            self.ui.treeView.setCurrentIndex(target_item.index())
            node_data = target_item.data(Qt.UserRole)
            try:
                self._current_node_id = int(node_data)
            except (TypeError, ValueError):
                self._current_node_id = self._root.node_id
        else:
            self._current_node_id = self._root.node_id
            self._display_children(self._root.node_id)
            return

        self._display_children(self._current_node_id)

    def _build_tree_items(self, node: FavoriteNode, parent_item: Optional[QStandardItem]) -> None:
        item = QStandardItem(node.name or "(未命名)")
        item.setEditable(False)
        item.setToolTip(node.path or node.name or "")
        item.setData(node.node_id, Qt.UserRole)
        self._item_index[node.node_id] = item

        if parent_item is None:
            self._tree_model.appendRow(item)
        else:
            parent_item.appendRow(item)

        for child in node.children:
            self._build_tree_items(child, item)

    def _apply_filter_to_list(self) -> None:
        self._list_model.clear()

        text = self._filter_text.lower()
        style = self.style()
        rows_added = 0

        for node in self._current_children:
            name_lower = (node.name or "").lower()
            path_lower = (node.path or "").lower()
            if text and text not in name_lower and text not in path_lower:
                continue

            item = QStandardItem(node.name or "(未命名)")
            item.setEditable(False)
            item.setIcon(style.standardIcon(QStyle.SP_DirIcon))
            item.setData(node.node_id, Qt.UserRole)
            item.setToolTip(node.path or "")
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
        current_item: QModelIndex = self.ui.treeView.currentIndex()
        current_item_name = current_item.data()
        logging.info(f"Creating new folder under: {current_item_name}")
        current_parent_id = self._current_node_id
        
        dialog = DialogFavoritesNewFolder(self, folder_path="新建文件夹", parent_node_id=current_parent_id)
        if dialog.exec() == QDialog.Accepted:
            self._reload_from_store()
            self._refresh_tree()

    def on_refresh(self) -> None:
        previous_id = self._current_node_id
        self._reload_from_store()
        if previous_id not in self._node_index:
            previous_id = self._root.node_id
        self._current_node_id = previous_id
        self._refresh_tree()

    def on_tree_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        node_id = current.data(Qt.UserRole)
        if node_id is None:
            node_id = self._root.node_id

        try:
            node_id = int(node_id)
        except (TypeError, ValueError):
            node_id = self._root.node_id

        self._current_node_id = node_id
        self._display_children(node_id)

    def on_tree_double_clicked(self, index: QModelIndex) -> None:
        node_id = index.data(Qt.UserRole)
        try:
            node_id = int(node_id)
        except (TypeError, ValueError):
            return

        node = self._node_index.get(node_id)
        if node and node.path:
            self._open_in_system(node.path)

    def on_tree_context_menu(self, point: QPoint) -> None:
        index = self.ui.treeView.indexAt(point)
        if not index.isValid():
            return

        node_id = index.data(Qt.UserRole)
        if node_id is None:
            return

        try:
            node_id_int = int(node_id)
        except (TypeError, ValueError):
            return

        node = self._node_index.get(node_id_int)
        if node is None:
            return

        menu = QMenu(self.ui.treeView)
        open_action = remove_action = None
        if node.path:
            open_action = menu.addAction("打开")
        if node_id_int != self._root.node_id:
            if open_action:
                menu.addSeparator()
            remove_action = menu.addAction("移除收藏")
        action = menu.exec(self.ui.treeView.mapToGlobal(point))
        if action == open_action and node.path:
            self._open_in_system(node.path)
        elif action == remove_action:
            self._remove_node(node_id_int)

    def on_list_item_double_clicked(self, index: QModelIndex) -> None:
        node_id = index.data(Qt.UserRole)
        try:
            node_id = int(node_id)
        except (TypeError, ValueError):
            return

        node = self._node_index.get(node_id)
        if node and node.path:
            self._open_in_system(node.path)

    def on_list_context_menu(self, point: QPoint) -> None:
        index = self.ui.listView.indexAt(point)
        if not index.isValid():
            return

        node_id = index.data(Qt.UserRole)
        if node_id is None:
            return

        try:
            node_id = int(node_id)
        except (TypeError, ValueError):
            return

        node = self._node_index.get(node_id)
        if node is None:
            return

        menu = QMenu(self.ui.listView)
        open_action = reveal_action = remove_action = None
        if node.path:
            open_action = menu.addAction("打开")
            reveal_action = menu.addAction("在资源管理器中显示")
        rename_action = menu.addAction("重命名")
        remove_action = menu.addAction("移除收藏")
		
        action = menu.exec(self.ui.listView.mapToGlobal(point))
        if action == open_action and node.path:
            self._open_in_system(node.path)
        elif action == reveal_action and node.path:
            self._reveal_in_explorer(node.path)
        elif action == remove_action:
            self._remove_node(node_id)
        elif action == rename_action:
            self._rename_node(node_id)

    def on_filter_text_changed(self, text: str) -> None:
        self._filter_text = text.strip()
        self._apply_filter_to_list()

    # ------------------------------------------------------------------
    # 数据与工具方法
    # ------------------------------------------------------------------
    def _display_children(self, node_id: int) -> None:
        node = self._node_index.get(node_id)
        self._current_children = list(node.children) if node else []
        self._apply_filter_to_list()

    def _find_parent_id(self, node_id: int) -> Optional[int]:
        for candidate_id, candidate in self._node_index.items():
            for child in candidate.children:
                if child.node_id == node_id:
                    return candidate_id
        return None

    def _remove_node(self, node_id: int, *, silent: bool = False) -> None:
        if node_id == self._root.node_id:
            if not silent:
                QMessageBox.information(self, "无法移除", "根收藏夹不能被移除。")
            return

        parent_id = self._find_parent_id(node_id) or self._root.node_id
        try:
            changed = self._store.remove_node(node_id)
        except Exception as exc:
            logging.exception("移除收藏失败: %s", node_id)
            QMessageBox.warning(self, "移除失败", f"写入收藏夹配置时发生错误：\n{exc}")
            return

        if not changed:
            if not silent:
                QMessageBox.information(self, "未移除", "未找到对应的收藏项目。")
            return

        self._current_node_id = parent_id
        self._reload_from_store()
        self._refresh_tree()
        if not silent:
            QMessageBox.information(self, "已移除", "收藏已移除。")
            
    def _rename_node(self, node_id: int) -> None:
        node = self._node_index.get(node_id)

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
