import logging
import os
import subprocess
import sys
from typing import Dict, List, Optional

from PySide6.QtCore import QModelIndex, QPoint, Qt
from PySide6.QtCore import QTimer
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemDelegate,
    QListView,
    QMenu,
    QMessageBox,
    QStyle,
    QWidget,
    QDialog, QAbstractItemView
)

from MuseLog.favorites_new_folder_dialog import DialogFavoritesNewFolder
from MuseLog.favorites_store import FavoritesStore
from MuseLog.model.node import FavoriteNode, NodeType
from MuseLog.ui.ui_tab_favorites import Ui_TabFavorites


class TabFavoritesWidget(QWidget):
    """Favorites manager supporting nested folders and quick navigation."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.ui = Ui_TabFavorites()
        self.ui.setupUi(self)

        self.ui.treeView.setHeaderHidden(True)
        self.ui.treeView.setUniformRowHeights(True)
        self.ui.treeView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.listView.setEditTriggers(
                QAbstractItemView.EditTrigger.EditKeyPressed
                | QAbstractItemView.EditTrigger.SelectedClicked
                | QAbstractItemView.EditTrigger.DoubleClicked
        )
        self.ui.listView.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.ui.listView.setUniformItemSizes(True)
        self.ui.listView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.lineFilter.setPlaceholderText("输入关键字以过滤右侧项目…")

        self._tree_model = QStandardItemModel(self.ui.treeView)
        self._tree_model.setHorizontalHeaderLabels(["收藏夹"])
        self.ui.treeView.setModel(self._tree_model)
        self._tree_model.itemChanged.connect(self._on_tree_item_changed)

        self._list_model = QStandardItemModel(self.ui.listView)
        self.ui.listView.setModel(self._list_model)
        self._list_model.itemChanged.connect(self._on_list_item_changed)

        tree_delegate = self.ui.treeView.itemDelegate()
        if isinstance(tree_delegate, QAbstractItemDelegate):
            tree_delegate.closeEditor.connect(self._on_editor_closed)  # type: ignore[attr-defined]
        list_delegate = self.ui.listView.itemDelegate()
        if isinstance(list_delegate, QAbstractItemDelegate):
            list_delegate.closeEditor.connect(self._on_editor_closed)  # type: ignore[attr-defined]

        self._store = FavoritesStore()
        self._root: FavoriteNode = self._store.get_root()
        self._node_index: Dict[int, FavoriteNode] = {}
        self._item_index: Dict[int, QStandardItem] = {}
        self._current_node_id: int = self._root.node_id
        self._current_children: List[FavoriteNode] = []
        self._filter_text: str = ""
        self._renaming_node_id: Optional[int] = None
        self._renaming_item: Optional[QStandardItem] = None
        self._renaming_original_name: str = ""
        self._renaming_model: Optional[QStandardItemModel] = None

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

        self._build_tree_items(self._root, None, NodeType.FOLDER)
        self.ui.treeView.expandAll()

        target_item = self._item_index.get(target_node_id) or self._item_index.get(self._root.node_id)
        if target_item is not None:
            self.ui.treeView.setCurrentIndex(target_item.index())
            node_data = target_item.data(Qt.ItemDataRole.UserRole)
            try:
                self._current_node_id = int(node_data)
            except (TypeError, ValueError):
                self._current_node_id = self._root.node_id
        else:
            self._current_node_id = self._root.node_id
        self._display_children(self._current_node_id)

    def _build_tree_items(self, node: FavoriteNode, parent_item: Optional[QStandardItem], filter_node_type: NodeType) -> None:
        if node.node_type != filter_node_type:
            return
        
        item = QStandardItem(node.name or "(未命名)")
        item.setEditable(False)
        item.setToolTip(node.path or node.name or "")
        item.setData(node.node_id, Qt.ItemDataRole.UserRole)
        self._item_index[node.node_id] = item

        if parent_item is None:
            self._tree_model.appendRow(item)
        else:
            parent_item.appendRow(item)

        for child in node.children:
            self._build_tree_items(child, item, filter_node_type)

    def _apply_filter_to_list(self) -> None:
        self._cancel_rename()
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
            if node.node_type == NodeType.FOLDER:
                item.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DirIcon))
            else:
                item.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_FileLinkIcon))
            item.setData(node.node_id, Qt.ItemDataRole.UserRole)
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
        current_parent_id = self._current_node_id if self._current_node_id in self._node_index else self._root.node_id
        current_item = self.ui.treeView.currentIndex()
        logging.info("Creating favorites folder under: %s", current_item.data())

        dialog = DialogFavoritesNewFolder(self, folder_path="新建文件夹", parent_node_id=current_parent_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._reload_from_store()
            self._refresh_tree()

    def on_refresh(self) -> None:
        target_id = self._current_node_id
        self._reload_from_store()
        if target_id not in self._node_index:
            target_id = self._root.node_id
        self._current_node_id = target_id
        self._refresh_tree()

    def on_tree_selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        node_id = current.data(Qt.ItemDataRole.UserRole)
        try:
            node_id = int(node_id)
        except (TypeError, ValueError):
            node_id = self._root.node_id
        self._current_node_id = node_id
        self._display_children(node_id)

    def on_tree_double_clicked(self, index: QModelIndex) -> None:
        node_id = index.data(Qt.ItemDataRole.UserRole)
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

        node_id = index.data(Qt.ItemDataRole.UserRole)
        try:
            node_id_int = int(node_id)
        except (TypeError, ValueError):
            return

        node = self._node_index.get(node_id_int)
        if node is None:
            return

        menu = QMenu(self.ui.treeView)
        open_action = remove_action = rename_action = None
        if node.path:
            open_action = menu.addAction("打开")
        if node_id_int != self._root.node_id:
            if open_action:
                menu.addSeparator()
            remove_action = menu.addAction("移除收藏")
            rename_action = menu.addAction("重命名")

        action = menu.exec(self.ui.treeView.mapToGlobal(point))
        if action == open_action and node.path:
            self._open_in_system(node.path)
        elif action == remove_action:
            self._remove_node(node_id_int)
        elif action == rename_action:
            self._rename_node(node_id_int)

    def on_list_item_double_clicked(self, index: QModelIndex) -> None:
        node_id = index.data(Qt.ItemDataRole.UserRole)
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

        node_id = index.data(Qt.ItemDataRole.UserRole)
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
        remove_action = menu.addAction("移除收藏")

        action = menu.exec(self.ui.listView.mapToGlobal(point))
        if action == open_action and node.path:
            self._open_in_system(node.path)
        elif action == reveal_action and node.path:
            self._reveal_in_explorer(node.path)
        elif action == remove_action:
            self._remove_node(node_id)

    def on_filter_text_changed(self, text: str) -> None:
        self._filter_text = text.strip()
        self._apply_filter_to_list()

    # ------------------------------------------------------------------
    # 数据与工具方法
    # ------------------------------------------------------------------
    def _display_children(self, node_id: int) -> None:
        node = self._node_index.get(node_id)
        self._current_children = list(node.children) if node else []
        # 只过滤显示 folder 节点
        # self._current_children = [child for child in node.children if child.node_type == NodeType.FOLDER] if node else []
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
        if node_id == self._root.node_id:
            QMessageBox.information(self, "无法重命名", "根收藏夹不支持重命名。")
            return

        item = self._item_index.get(node_id)
        if item is None:
            QMessageBox.information(self, "无法重命名", "未找到对应的收藏节点。")
            return

        self._cancel_rename()
        self._renaming_node_id = node_id
        self._renaming_item = item
        self._renaming_original_name = item.text()
        self._renaming_model = self._tree_model

        item.setEditable(True)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        
        index = item.index()
        if index.column() != 0:  # 保险：只让第0列进入编辑
            index = index.siblingAtColumn(0)
        try:
            self.ui.treeView.setCurrentIndex(index)
            self.ui.treeView.scrollTo(index)
            self.ui.treeView.setFocus()
            # 关键：把 edit 延迟到下一个事件循环，避免“editing failed”
            QTimer.singleShot(0, lambda: self.ui.treeView.edit(index))
        except Exception as e:
            logging.error("Failed to edit item: %s", e)

    def _cancel_rename(self) -> None:
        if self._renaming_item is None:
            return

        model = self._renaming_model or self._tree_model
        was_blocked = model.signalsBlocked()
        model.blockSignals(True)
        self._renaming_item.setText(self._renaming_original_name)
        self._renaming_item.setEditable(False)
        model.blockSignals(was_blocked)
        self._clear_rename_state()

    def _on_list_item_changed(self, item: QStandardItem) -> None:
        self._handle_item_renamed(item)

    def _on_tree_item_changed(self, item: QStandardItem) -> None:
        self._handle_item_renamed(item)

    def _handle_item_renamed(self, item: QStandardItem) -> None:
        if self._renaming_node_id is None or item is not self._renaming_item:
            return

        new_name = item.text().strip()
        if not new_name:
            QMessageBox.warning(self, "重命名失败", "收藏名称不能为空。")
            self._cancel_rename()
            return

        if new_name == self._renaming_original_name:
            self._cancel_rename()
            return

        parent_id = self._find_parent_id(self._renaming_node_id) or self._root.node_id
        parent_node = self._node_index.get(parent_id)
        if parent_node:
            for child in parent_node.children:
                if child.node_id != self._renaming_node_id and child.name.lower() == new_name.lower():
                    QMessageBox.warning(self, "重命名失败", "同一层级中已存在相同名称。")
                    self._cancel_rename()
                    return

        try:
            self._store.rename_node(self._renaming_node_id, new_name)
        except ValueError as exc:
            QMessageBox.warning(self, "重命名失败", str(exc))
            self._cancel_rename()
            return
        except KeyError:
            QMessageBox.warning(self, "重命名失败", "未找到对应的收藏节点。")
            self._cancel_rename()
            return
        except Exception as exc:  # pragma: no cover - defensive
            logging.exception("重命名收藏失败: %s", self._renaming_node_id)
            QMessageBox.warning(self, "重命名失败", f"写入收藏夹配置时发生错误：\n{exc}")
            self._cancel_rename()
            return

        renamed_node_id = self._renaming_node_id
        self._clear_rename_state()
        self._current_node_id = renamed_node_id
        self._reload_from_store()
        self._refresh_tree()

    def _clear_rename_state(self) -> None:
        if self._renaming_item is not None:
            self._renaming_item.setEditable(False)
        self._renaming_node_id = None
        self._renaming_item = None
        self._renaming_original_name = ""
        self._renaming_model = None

    def _on_editor_closed(self, _editor: QWidget, hint: QAbstractItemDelegate.EndEditHint) -> None:
        if self._renaming_node_id is None:
            return
        if hint == QAbstractItemDelegate.EndEditHint.RevertModelCache:
            self._cancel_rename()
        elif hint == QAbstractItemDelegate.EndEditHint.NoHint:
            if self._renaming_item is not None and self._renaming_item.isEditable():
                self._renaming_item.setEditable(False)

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
