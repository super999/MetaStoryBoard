import logging
import os
import json
from typing import Dict, Any, List, Optional, Sequence

from PySide6.QtCore import QDir, QModelIndex
from PySide6.QtWidgets import (
    QWidget, QFileSystemModel, QMessageBox, QTableWidgetItem
)

from MuseLog.ui.ui_tab_explorer import Ui_TabExplorer
from PySide6.QtWidgets import QHBoxLayout, QHeaderView, QPushButton

from MuseLog.explorer_custom_widgets import resolve_custom_widget_builder
from MuseLog.explorer_signals import signal_manager


class MetaStruct:
    def __init__(self, name: str, file_path: str = "", op_type: str = "", op_name: str = "", op_data: Any = None):
        self.name = name
        self.file_path = file_path
        self.op_type = op_type
        self.op_name = op_name
        self.op_data = op_data


class TabExplorerWidget(QWidget):
    """
    资源管理器风格的标签页：
    - 顶部地址栏可输入目录路径，点击"进入"导航
    - 左侧树形目录（仅显示文件夹）
    - 右侧展示所选目录的元数据信息（提示词、模型、视频文件、参考图等）
    - 支持历史路径导航和刷新功能
    """

    def __init__(self, parent=None, default_path: Optional[str] = None):
        super().__init__(parent)
        self.ui = Ui_TabExplorer()
        self.ui.setupUi(self)

        # 文件系统模型（仅目录）
        self.model = QFileSystemModel(self)
        self.model.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)
        self.model.setRootPath("")

        self.ui.treeView.setModel(self.model)
        # 仅显示第一列名称，其余列隐藏
        for col in range(1, 4):
            self.ui.treeView.setColumnHidden(col, True)

        # 初始化 表格 TableWidget
        hh = self.ui.tableMeta.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.Fixed)
        self.ui.tableMeta.setColumnWidth(1, 400)

        # 绑定事件
        self.ui.btnEnter.clicked.connect(self.on_enter_clicked)
        self.ui.lineAddress.returnPressed.connect(self.on_enter_clicked)
        self.ui.treeView.selectionModel().selectionChanged.connect(self.on_tree_selection_changed)
        self.ui.btnReference.clicked.connect(self.on_reference_clicked)
        self.ui.btnSequenceFrames.clicked.connect(self.on_sequence_frames_clicked)
        self.ui.btnSpine.clicked.connect(self.on_spine_clicked)
        self.ui.btnVideo.clicked.connect(self.on_video_clicked)
        self.ui.btnBack.clicked.connect(self.on_back_clicked)
        self.ui.btnGoUp.clicked.connect(self.on_go_up_clicked)
        self.ui.btnRefresh.clicked.connect(self.on_refresh_clicked)

        # 绑定信号
        signal_manager.delete_selected_animation_sequence.connect(self.on_delete_selected_animation_sequence)
        signal_manager.rename_folder.connect(self.on_update_animation_sequence)

        self._history: List[str] = []
        self._history_limit: int = 50
        self._current_path: Optional[str] = None
        self._suppress_tree_selection: bool = False
        self._suppress_history: bool = False

        self._update_nav_buttons()

        self._config_file = self._init_config_path()
        last_path = self._load_last_path()

        # 初始化地址，优先使用记录的历史路径
        start_candidates = [last_path, default_path, QDir.homePath()]
        chosen_path: Optional[str] = None
        for candidate in start_candidates:
            if candidate and os.path.isdir(candidate):
                chosen_path = candidate
                break
        if not chosen_path:
            chosen_path = QDir.homePath()
        self.navigate_to_path(chosen_path)

    # ---------------------- 导航与选择 ----------------------
    def on_enter_clicked(self):
        path = self.ui.lineAddress.text().strip()
        self.navigate_to_path(path)

    def navigate_to_path(self, path: str, *, add_history: bool = True, update_tree: bool = True):
        if not path:
            return
        path = os.path.normpath(path)
        # 若输入的是文件，则转为其父目录
        if os.path.isfile(path):
            path = os.path.dirname(path)
        if not os.path.exists(path) or not os.path.isdir(path):
            QMessageBox.warning(self, "无效路径", f"目录不存在：\n{path}", QMessageBox.Ok)
            return
        self.ui.lineAddress.setText(path)
        idx = self.model.index(path)
        if not idx.isValid():
            idx = self.model.setRootPath(path)
        if update_tree:
            self._suppress_tree_selection = True
            try:
                self.ui.treeView.setRootIndex(idx)
                # 自动选中根目录，刷新右侧信息
                self.ui.treeView.setCurrentIndex(idx)
            finally:
                self._suppress_tree_selection = False
        self.show_directory_metadata(path)
        self._save_last_path(path)
        self._set_current_path(path, add_history=add_history)

    def on_tree_selection_changed(self, selected, _deselected):
        if self._suppress_tree_selection:
            return
        indexes: List[QModelIndex] = selected.indexes()
        if not indexes:
            return
        idx = indexes[0]
        path = self.model.filePath(idx)
        if os.path.isfile(path):
            path = os.path.dirname(path)
        if os.path.isdir(path):
            self.ui.lineAddress.setText(path)
            self.show_directory_metadata(path)
            self._set_current_path(path, add_history=True)
            self._save_last_path(path)

    def on_back_clicked(self):
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

    def on_go_up_clicked(self):
        current_path = self._current_path or self.ui.lineAddress.text().strip()
        if not current_path:
            return
        if not os.path.isdir(current_path):
            current_path = os.path.dirname(current_path)
        dir_obj = QDir(current_path)
        if not dir_obj.exists():
            # 若当前目录不存在，则寻找最近的有效父目录
            parent_path = self._find_existing_parent(current_path)
            if not parent_path:
                return
            dir_obj = QDir(parent_path)
        if not dir_obj.cdUp():
            return
        parent = os.path.normpath(dir_obj.absolutePath())
        self.navigate_to_path(parent)

    def on_refresh_clicked(self):
        current_path = self._current_path or self.ui.lineAddress.text().strip()
        if not current_path or not os.path.isdir(current_path):
            return
        try:
            idx = self.model.index(current_path)
            if hasattr(self.model, "refresh"):
                if idx.isValid():
                    self.model.refresh(idx)
                else:
                    self.model.refresh()
        except Exception:
            pass
        self.navigate_to_path(current_path, add_history=False, update_tree=True)

    # ---------------------- 元数据收集与显示 ----------------------
    def show_directory_metadata(self, folder: str):
        meta: Dict[str, MetaStruct] = self.collect_metadata(folder)
        self._update_custom_widget(folder, meta)
        self.populate_table(meta)

    def populate_table(self, meta: Dict[str, MetaStruct]):
        self.ui.tableMeta.clearContents()
        rows = []
        # 友好排序
        key_order = [
            "目录", "提示词", "模型名称", "视频文件", "参考图",
        ]
        for k in key_order:
            if k in meta:
                rows.append((k, meta[k]))
        # 其他键
        existing = {k for k, _ in rows}
        for k, v in meta.items():
            if k not in existing:
                rows.append((k, v))

        self.ui.tableMeta.setRowCount(len(rows))
        k: str
        v: MetaStruct
        for i, (k, v) in enumerate(rows):
            v_str = v.name
            v_op = v.op_type
            self.ui.tableMeta.setItem(i, 0, QTableWidgetItem(str(k)))
            self.ui.tableMeta.setItem(i, 1, QTableWidgetItem(v_str))
            if v_op:                
                button = QPushButton(v.op_name, self.ui.tableMeta)
                button.clicked.connect(lambda _, op=v.op_data: self.on_metadata_operation_clicked(v_op, op))
                # 直接把 button 设置到 table 的指定位置
                self.ui.tableMeta.setCellWidget(i, 2, button)
        self.ui.tableMeta.resizeColumnToContents(0)

    def collect_metadata(self, folder: str) -> Dict[str, MetaStruct]:
        meta: Dict[str, MetaStruct]={"目录": MetaStruct(folder)}
        # 1) 常见的提示词 / 参数文件
        prompt_text=self._read_first_text([
            os.path.join(folder, name) for name in (
                "prompt.txt", "prompts.txt", "neg_prompt.txt", "caption.txt"
            )
        ])
        if prompt_text:
            meta["提示词"]=MetaStruct("提示词", prompt_text.strip()[:2000])

        # 2) 常见 JSON 参数/元数据
        json_data=self._read_first_json([
            os.path.join(folder, name) for name in (
                "metadata.json", "params.json", "info.json"
            )
        ])
        if json_data:
            # 直接解析常用键
            model=json_data.get("model") or json_data.get("model_name") or json_data.get("ckpt")
            if model:
                meta["模型名称"]=MetaStruct("模型名称", model)
            # 如果 JSON 本身就包含 prompt，也补上
            if "prompt" in json_data and "提示词" not in meta:
                meta["提示词"]=MetaStruct("提示词", str(json_data.get("prompt"))[:2000])
            meta["其他参数"]=MetaStruct("其他参数", json_data)

        # 3) 视频文件列表
        videos=self._list_files(folder, exts={".mp4", ".mov", ".avi", ".mkv", ".webm"})
        if videos:
            for i, video in enumerate(videos):
                meta[f'视频文件_{i}']=MetaStruct(os.path.basename(video), op_type='视频元数据', op_name='元数据', op_data=video)

        # 4) 参考图（文件名包含 ref/reference，或在 ref/ 子目录）
        refs=[]
        images=self._list_files(folder, exts={".png", ".jpg", ".jpeg", ".bmp", ".gif"})
        for p in images:
            name=os.path.basename(p).lower()
            if ("ref" in name) or ("reference" in name):
                refs.append(p)
        ref_dir=os.path.join(folder, "ref")
        if os.path.isdir(ref_dir):
            refs.extend(self._list_files(ref_dir, exts={".png", ".jpg", ".jpeg", ".bmp", ".gif"}))
        if refs:
            meta["参考图"]=MetaStruct("参考图", ", ".join(os.path.basename(r) for r in refs[:20]) + (" ..." if len(refs) > 20 else ""))

        return meta

    # ---------------------- 导航辅助 ----------------------
    def _set_current_path(self, path: str, add_history: bool=True) -> None:
        if not path:
            return
        normalized_new=self._normalize_path(path)
        normalized_current=self._normalize_path(self._current_path)
        if add_history and self._current_path and normalized_new != normalized_current:
            if not self._history or self._normalize_path(self._history[-1]) != normalized_current:
                self._history.append(self._current_path)
                self._trim_history()
        self._current_path=path
        self._update_nav_buttons()

    def _normalize_path(self, path: Optional[str]) -> Optional[str]:
        if not path:
            return None
        return os.path.normcase(os.path.normpath(path))

    def _trim_history(self) -> None:
        if len(self._history) > self._history_limit:
            overflow=len(self._history) - self._history_limit
            if overflow > 0:
                del self._history[0:overflow]

    def _update_custom_widget(self, folder: str, meta: Dict[str, MetaStruct]) -> None:
        """根据选中目录动态调整自定义展示区域."""
        logging.info("[TabExplorer] 选中目录: %s", folder)
        builder=resolve_custom_widget_builder(folder, meta)
        widgets=builder(self.ui.widget_custom_show, folder, meta) if builder else []
        self._apply_custom_widgets(widgets)

    def _apply_custom_widgets(self, widgets: Sequence[QWidget]) -> None:
        container=self.ui.widget_custom_show
        layout=container.layout()
        if layout is None:
            layout=QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(8)

        self._clear_custom_widget(layout)

        for widget in widgets:
            if widget.parent() is not container:
                widget.setParent(container)
            layout.addWidget(widget)
            widget.show()

        container.setVisible(bool(widgets))

    def _clear_custom_widget(self, layout: QHBoxLayout) -> None:
        while layout.count():
            item=layout.takeAt(0)
            widget=item.widget()
            if widget is not None:
                widget.deleteLater()


    def _find_existing_parent(self, path: str) -> Optional[str]:
        candidate=os.path.normpath(path)
        visited=set()
        while True:
            normalized_candidate=self._normalize_path(candidate)
            if normalized_candidate in visited:
                return None
            visited.add(normalized_candidate)
            if os.path.isdir(candidate):
                return candidate
            parent=os.path.dirname(candidate)
            if not parent or self._normalize_path(parent) == normalized_candidate:
                return None
            candidate=parent

    def _update_nav_buttons(self) -> None:
        self.ui.btnBack.setEnabled(bool(self._history))
        current=self._current_path
        current_exists=bool(current and os.path.isdir(current))
        can_go_up=False
        if current_exists:
            dir_obj=QDir(current)
            can_go_up=dir_obj.cdUp()
        self.ui.btnGoUp.setEnabled(can_go_up)
        self.ui.btnRefresh.setEnabled(current_exists)

    # ---------------------- 工具函数 ----------------------
    def _read_first_text(self, paths: List[str]) -> Optional[str]:
        for p in paths:
            try:
                if os.path.isfile(p):
                    with open(p, "r", encoding="utf-8") as f:
                        return f.read()
            except Exception:
                # 尝试 gbk 兼容
                try:
                    with open(p, "r", encoding="gbk", errors="ignore") as f:
                        return f.read()
                except Exception:
                    pass
        return None

    def _read_first_json(self, paths: List[str]) -> Optional[Dict[str, Any]]:
        for p in paths:
            try:
                if os.path.isfile(p):
                    with open(p, "r", encoding="utf-8") as f:
                        return json.load(f)
            except Exception:
                continue
        return None

    def _list_files(self, folder: str, exts: set[str]) -> List[str]:
        out: List[str]=[]
        try:
            for name in os.listdir(folder):
                p=os.path.join(folder, name)
                if os.path.isfile(p):
                    _, ext=os.path.splitext(name)
                    if ext.lower() in exts:
                        out.append(p)
        except Exception:
            pass
        return out

    # ---------------------- 状态持久化 ----------------------
    def _init_config_path(self) -> str:
        config_dir=os.path.join(os.path.expanduser("~"), ".muselog")
        try:
            os.makedirs(config_dir, exist_ok=True)
        except Exception:
            pass
        return os.path.join(config_dir, "tab_explorer.json")

    def _load_last_path(self) -> Optional[str]:
        try:
            with open(self._config_file, "r", encoding="utf-8") as f:
                data=json.load(f)
            path=data.get("last_path")
            if path and os.path.isdir(path):
                return path
        except Exception:
            pass
        return None

    def _save_last_path(self, path: str) -> None:
        if not path:
            return
        try:
            os.makedirs(os.path.dirname(self._config_file), exist_ok=True)
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump({"last_path": path}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def on_reference_clicked(self):
        # 检查当前目录下是否有 “参考图” 的子目录
        current_path=self.ui.lineAddress.text().strip()
        ref_dir=os.path.join(current_path, "参考图")
        if os.path.isdir(ref_dir):
            self.navigate_to_path(ref_dir)
        else:
            # 若没有，则创建该目录，并导航过去
            try:
                os.makedirs(ref_dir, exist_ok=True)
                self.navigate_to_path(ref_dir)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法创建参考图目录：\n{str(e)}", QMessageBox.Ok)

    # on_sequence_frames_clicked
    def on_sequence_frames_clicked(self):
        current_path=self.ui.lineAddress.text().strip()
        seq_dir=os.path.join(current_path, "序列帧")
        if os.path.isdir(seq_dir):
            self.navigate_to_path(seq_dir)
        else:
            try:
                os.makedirs(seq_dir, exist_ok=True)
                self.navigate_to_path(seq_dir)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法创建序列帧目录：\n{str(e)}", QMessageBox.Ok)

    # on_spine_clicked
    def on_spine_clicked(self):
        current_path=self.ui.lineAddress.text().strip()
        spine_dir=os.path.join(current_path, "Spine")
        if os.path.isdir(spine_dir):
            self.navigate_to_path(spine_dir)
        else:
            try:
                os.makedirs(spine_dir, exist_ok=True)
                self.navigate_to_path(spine_dir)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法创建Spine目录：\n{str(e)}", QMessageBox.Ok)

    # on_video_clicked
    def on_video_clicked(self):
        current_path=self.ui.lineAddress.text().strip()
        video_dir=os.path.join(current_path, "视频")
        if os.path.isdir(video_dir):
            self.navigate_to_path(video_dir)
        else:
            try:
                os.makedirs(video_dir, exist_ok=True)
                self.navigate_to_path(video_dir)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法创建视频目录：\n{str(e)}", QMessageBox.Ok)

    def on_delete_selected_animation_sequence(self):
        logging.info(f"删除选中的动画序列, 当前选中路径: {self._current_path}")
        # 删除指定的文件夹，并刷新目录
        if not self._current_path:
            return
        try:
            if os.path.isdir(self._current_path):
                import shutil
                shutil.rmtree(self._current_path)
                logging.info(f"已删除目录: {self._current_path}")
                # 刷新当前目录的上级目录
                parent_dir=os.path.dirname(self._current_path)
                self.navigate_to_path(parent_dir, add_history=False)
        except Exception as e:
            logging.error(f"删除目录失败: {self._current_path}, 错误: {str(e)}")


    # rename_folder = Signal(str, str)
    def on_update_animation_sequence(self, old_folder_name: str, new_folder_name: str):
        logging.info(f"重命名动画序列文件夹: {old_folder_name} -> {new_folder_name}")
        if not self._current_path:
            return
        try:
            os.rename(old_folder_name, new_folder_name)
            logging.info(f"已重命名目录: {old_folder_name} -> {new_folder_name}")
            parent_dir=os.path.dirname(old_folder_name)
            self.navigate_to_path(parent_dir, add_history=False)
            logging.info(f"已导航到父目录: {parent_dir}")
        except Exception as e:
            logging.error(f"重命名目录失败: {old_folder_name} -> {new_folder_name}, 错误: {str(e)}")
            
    def on_metadata_operation_clicked(self, op_type: str, op_data: Any):
        if op_type == "视频元数据":
            video_path=str(op_data)
            logging.info(f"显示视频元数据: {video_path}")
            # 在 detailWidget 中 加载 widget 
            
            self.ui.DetailWidget
        # 其他操作类型可在此扩展