from __future__ import annotations

import logging
import os
from typing import Optional

from PySide6.QtCore import QDir, Qt
from PySide6.QtWidgets import (
    QFileSystemModel,
    QHBoxLayout,
    QHeaderView,
    QMenu,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from MuseLog.explorer.detail_mixin import DetailMixin
from MuseLog.explorer.meta import MetaStruct
from MuseLog.explorer.metadata_mixin import MetadataMixin
from MuseLog.explorer.navigation_mixin import NavigationMixin
from MuseLog.explorer.persistence_mixin import PersistenceMixin
from MuseLog.explorer_custom_widgets import resolve_custom_widget_builder
from MuseLog.explorer_signals import signal_manager
from MuseLog.favorites_store import FavoriteNode, FavoritesStore
from MuseLog.ui.ui_tab_explorer import Ui_TabExplorer
from MuseLog.widget_video_detail import VideoDetailWidget


class TabExplorerWidget(
    QWidget,
    DetailMixin,
    MetadataMixin,
    NavigationMixin,
    PersistenceMixin,
):
    """Explorer-style tab with navigation, metadata, and custom widgets."""

    def __init__(self, parent: Optional[QWidget] = None, default_path: Optional[str] = None) -> None:
        super().__init__(parent)
        self.ui = Ui_TabExplorer()
        self.ui.setupUi(self)

        self.model = QFileSystemModel(self)
        self.model.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)
        self.model.setRootPath("")

        self.ui.treeView.setModel(self.model)
        for column in range(1, 4):
            self.ui.treeView.setColumnHidden(column, True)

        header = self.ui.tableMeta.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        self.ui.tableMeta.setColumnWidth(1, 400)

        self._favorites_store = FavoritesStore()
        self._video_detail_widget: Optional[VideoDetailWidget] = None

        self._init_navigation_state()
        self._init_metadata_state()
        self._init_detail_layout()

        self._bind_signals()
        self._update_nav_buttons()

        self._config_file = self._init_config_path()
        last_path = self._load_last_path()

        start_candidates = [last_path, default_path, QDir.homePath()]
        chosen_path: Optional[str] = None
        for candidate in start_candidates:
            if candidate and os.path.isdir(candidate):
                chosen_path = candidate
                break
        if not chosen_path:
            chosen_path = QDir.homePath()
        self.navigate_to_path(chosen_path)

    # ------------------------------------------------------------------
    # UI wiring
    # ------------------------------------------------------------------
    def _bind_signals(self) -> None:
        self.ui.btnEnter.clicked.connect(self.on_enter_clicked)
        self.ui.lineAddress.returnPressed.connect(self.on_enter_clicked)
        self.ui.treeView.selectionModel().selectionChanged.connect(self.on_tree_selection_changed)
        self.ui.tableMeta.cellClicked.connect(self.on_table_cell_activated)

        self.ui.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.treeView.customContextMenuRequested.connect(self.on_tree_context_menu)

        self.ui.btnReference.clicked.connect(self.on_reference_clicked)
        self.ui.btnSequenceFrames.clicked.connect(self.on_sequence_frames_clicked)
        self.ui.btnSpine.clicked.connect(self.on_spine_clicked)
        self.ui.btnVideo.clicked.connect(self.on_video_clicked)
        self.ui.btnSizeModify.clicked.connect(self.on_size_modify_clicked)

        self.ui.btnBack.clicked.connect(self.on_back_clicked)
        self.ui.btnGoUp.clicked.connect(self.on_go_up_clicked)
        self.ui.btnRefresh.clicked.connect(self.on_refresh_clicked)

        signal_manager.delete_selected_animation_sequence.connect(self.on_delete_selected_animation_sequence)
        signal_manager.rename_folder.connect(self.on_update_animation_sequence)

    # ------------------------------------------------------------------
    # Context menu & actions
    # ------------------------------------------------------------------
    def on_tree_context_menu(self, point) -> None:  # type: ignore[override]
        index = self.ui.treeView.indexAt(point)
        if not index.isValid():
            return

        folder_path = self.model.filePath(index)
        if not folder_path or not os.path.isdir(folder_path):
            return

        menu = QMenu(self.ui.treeView)
        delete_action = menu.addAction("删除文件夹")
        favorite_action = menu.addAction("收藏此文件夹")
        action = menu.exec(self.ui.treeView.viewport().mapToGlobal(point))
        if action == delete_action:
            self._confirm_delete_folder(folder_path)
        elif action == favorite_action:
            self._add_to_favorites(folder_path)

    def _add_to_favorites(self, folder_path: str) -> None:
        normalized = os.path.normpath(folder_path)
        if not os.path.isdir(normalized):
            QMessageBox.warning(self, "收藏失败", f"目录不存在：\n{normalized}", QMessageBox.Ok)
            return

        existing = self._find_favorite_node_by_path(normalized)
        if existing:
            QMessageBox.information(self, "已存在", f"该目录已在收藏列表中：\n{existing.name}", QMessageBox.Ok)
            return

        try:
            node = self._favorites_store.add_leaf_node(normalized)
        except FileNotFoundError:
            QMessageBox.warning(self, "收藏失败", f"目录不存在：\n{normalized}", QMessageBox.Ok)
            return
        except Exception as exc:  # pragma: no cover - defensive
            logging.exception("添加收藏失败: %s", normalized)
            QMessageBox.critical(self, "收藏失败", f"写入收藏配置时发生错误：\n{exc}")
            return

        alias = node.name if isinstance(node, FavoriteNode) else os.path.basename(normalized)
        QMessageBox.information(self, "已收藏", f"目录已加入收藏：\n{alias}", QMessageBox.Ok)

    def _confirm_delete_folder(self, folder_path: str) -> None:
        normalized_path = os.path.normpath(folder_path)
        if not os.path.isdir(normalized_path):
            QMessageBox.warning(self, "删除失败", f"目录不存在：\n{normalized_path}", QMessageBox.Ok)
            return

        parent_dir = os.path.dirname(normalized_path)
        if not parent_dir or os.path.normcase(parent_dir) == os.path.normcase(normalized_path):
            QMessageBox.warning(self, "删除失败", "无法删除根目录。", QMessageBox.Ok)
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除以下目录及其全部内容吗？\n{normalized_path}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            import shutil

            shutil.rmtree(normalized_path)
        except Exception as exc:
            logging.exception("删除目录失败: %s", normalized_path)
            QMessageBox.critical(self, "删除失败", f"删除目录时发生错误：\n{normalized_path}\n错误：{exc}")
            return

        logging.info("已删除目录: %s", normalized_path)
        normalized_removed = self._normalize_path(normalized_path)
        self._history = [path for path in self._history if self._normalize_path(path) != normalized_removed]

        if self._normalize_path(self._current_path) == normalized_removed:
            self._current_path = None
            self._clear_detail_widget()

        target_dir = parent_dir if os.path.isdir(parent_dir) else self._find_existing_parent(parent_dir)
        if not target_dir:
            target_dir = QDir.homePath()
        self.navigate_to_path(target_dir, add_history=False)

    # ------------------------------------------------------------------
    # Custom widgets & metadata ops
    # ------------------------------------------------------------------
    def _update_custom_widget(self, folder: str, meta: dict[str, MetaStruct]) -> None:
        logging.info("[TabExplorer] 选中目录: %s", folder)
        builder = resolve_custom_widget_builder(folder, meta)
        widgets = builder(self.ui.widget_custom_show, folder, meta) if builder else []
        self._apply_custom_widgets(widgets)

    def on_metadata_operation_clicked(self, op_type: str, op_data) -> None:  # type: ignore[override]
        if op_type == "视频元数据":
            video_path = str(op_data)
            logging.info("显示视频元数据: %s", video_path)
            if self._video_detail_widget is None:
                self._video_detail_widget = VideoDetailWidget(self.ui.DetailWidget)
                self._video_detail_widget.notify_close.connect(self._clear_detail_widget)
            self._video_detail_widget.set_video(video_path)
            self._show_detail_widget(self._video_detail_widget)
            return
        if op_type == "打开文本文件":
            file_path = str(op_data)
            logging.info("打开文本文件: %s", file_path)
            try:
                if os.path.isfile(file_path):
                    os.startfile(file_path)  # type: ignore[attr-defined]
                else:
                    QMessageBox.warning(self, "文件不存在", f"文件不存在：\n{file_path}", QMessageBox.Ok)
            except Exception as exc:
                QMessageBox.warning(self, "读取文件失败", f"无法读取文件：\n{file_path}\n错误：{exc}", QMessageBox.Ok)
            return
        if op_type == "打开文件夹":
            folder_path = str(op_data)
            logging.info("打开文件夹: %s", folder_path)
            try:
                os.startfile(folder_path)  # type: ignore[attr-defined]
            except Exception as exc:
                QMessageBox.warning(self, "打开文件夹失败", f"无法打开文件夹：\n{folder_path}\n错误：{exc}", QMessageBox.Ok)
            return
        logging.debug("未处理的元数据操作类型: %s", op_type)

    # ------------------------------------------------------------------
    # Navigation helpers
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Quick access buttons
    # ------------------------------------------------------------------
    def on_reference_clicked(self) -> None:
        current_path = self.ui.lineAddress.text().strip()
        ref_dir = os.path.join(current_path, "参考图")
        self._ensure_folder_and_navigate(ref_dir)

    def on_sequence_frames_clicked(self) -> None:
        current_path = self.ui.lineAddress.text().strip()
        seq_dir = os.path.join(current_path, "序列帧")
        self._ensure_folder_and_navigate(seq_dir)

    def on_spine_clicked(self) -> None:
        current_path = self.ui.lineAddress.text().strip()
        spine_dir = os.path.join(current_path, "Spine")
        self._ensure_folder_and_navigate(spine_dir)

    def on_video_clicked(self) -> None:
        current_path = self.ui.lineAddress.text().strip()
        video_dir = os.path.join(current_path, "视频")
        self._ensure_folder_and_navigate(video_dir)

    def on_size_modify_clicked(self) -> None:
        current_path = self.ui.lineAddress.text().strip()
        size_modify_dir = os.path.join(current_path, "尺寸修改")
        self._ensure_folder_and_navigate(size_modify_dir)

    def _ensure_folder_and_navigate(self, target_dir: str) -> None:
        if os.path.isdir(target_dir):
            self.navigate_to_path(target_dir)
            return
        try:
            os.makedirs(target_dir, exist_ok=True)
            self.navigate_to_path(target_dir)
        except Exception as exc:
            QMessageBox.warning(self, "错误", f"无法创建目录：\n{exc}", QMessageBox.Ok)

    # ------------------------------------------------------------------
    # Signal callbacks
    # ------------------------------------------------------------------
    def on_delete_selected_animation_sequence(self) -> None:
        logging.info("删除选中的动画序列, 当前选中路径: %s", self._current_path)
        if not self._current_path:
            return
        try:
            if os.path.isdir(self._current_path):
                import shutil

                shutil.rmtree(self._current_path)
                logging.info("已删除目录: %s", self._current_path)
                parent_dir = os.path.dirname(self._current_path)
                self.navigate_to_path(parent_dir, add_history=False)
        except Exception as exc:
            logging.error("删除目录失败: %s, 错误: %s", self._current_path, exc)

    def on_update_animation_sequence(self, old_folder_name: str, new_folder_name: str) -> None:
        logging.info("重命名动画序列文件夹: %s -> %s", old_folder_name, new_folder_name)
        if not self._current_path:
            return
        try:
            os.rename(old_folder_name, new_folder_name)
            logging.info("已重命名目录: %s -> %s", old_folder_name, new_folder_name)
            parent_dir = os.path.dirname(old_folder_name)
            self.navigate_to_path(parent_dir, add_history=False)
            logging.info("已导航到父目录: %s", parent_dir)
        except Exception as exc:
            logging.error("重命名目录失败: %s -> %s, 错误: %s", old_folder_name, new_folder_name, exc)

    # ------------------------------------------------------------------
    # Overrides expected by mixins
    # ------------------------------------------------------------------
    def show_directory_metadata(self, folder: str) -> None:  # type: ignore[override]
        meta = self.collect_metadata(folder)
        self._clear_detail_widget()
        self._update_custom_widget(folder, meta)
        self.populate_table(meta)

    def _find_existing_parent(self, path: str) -> Optional[str]:  # type: ignore[override]
        candidate = os.path.normpath(path)
        visited: set[str] = set()
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

    def _find_favorite_node_by_path(self, path: str) -> Optional[FavoriteNode]:
        normalized_target = self._normalize_path(path)
        try:
            root = self._favorites_store.get_root()
        except Exception:
            return None

        stack: list[FavoriteNode] = [root]
        while stack:
            node = stack.pop()
            if node.path and self._normalize_path(node.path) == normalized_target:
                return node
            stack.extend(node.children)
        return None
