import os
import json
from typing import Dict, Any, List, Optional

from PySide6.QtCore import QDir, QModelIndex
from PySide6.QtWidgets import (
    QWidget, QFileSystemModel, QMessageBox, QTableWidgetItem
)

from MuseLog.ui.ui_tab_explorer import Ui_TabExplorer


class TabExplorerWidget(QWidget):
    """
    资源管理器风格的标签页：
    - 顶部地址栏可输入目录路径，点击“进入”导航
    - 左侧树形目录（仅显示文件夹）
    - 右侧展示所选目录的元数据信息（提示词、模型、视频文件、参考图等）
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

        # 绑定事件
        self.ui.btnEnter.clicked.connect(self.on_enter_clicked)
        self.ui.lineAddress.returnPressed.connect(self.on_enter_clicked)
        self.ui.treeView.selectionModel().selectionChanged.connect(self.on_tree_selection_changed)
        self.ui.btnReference.clicked.connect(self.on_reference_clicked)
        self.ui.btnSequenceFrames.clicked.connect(self.on_sequence_frames_clicked)
        self.ui.btnSpine.clicked.connect(self.on_spine_clicked)
        self.ui.btnVideo.clicked.connect(self.on_video_clicked)

        # 初始化地址
        start_path = default_path or QDir.homePath()
        self.navigate_to_path(start_path)

    # ---------------------- 导航与选择 ----------------------
    def on_enter_clicked(self):
        path = self.ui.lineAddress.text().strip()
        self.navigate_to_path(path)

    def navigate_to_path(self, path: str):
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
        self.ui.treeView.setRootIndex(idx)
        # 自动选中根目录，刷新右侧信息
        self.ui.treeView.setCurrentIndex(idx)
        self.show_directory_metadata(path)

    def on_tree_selection_changed(self, selected, _deselected):
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

    # ---------------------- 元数据收集与显示 ----------------------
    def show_directory_metadata(self, folder: str):
        meta = self.collect_metadata(folder)
        self.populate_table(meta)

    def populate_table(self, meta: Dict[str, Any]):
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
        for i, (k, v) in enumerate(rows):
            v_str = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, indent=2) if isinstance(v, (dict, list)) else str(v)
            self.ui.tableMeta.setItem(i, 0, QTableWidgetItem(str(k)))
            self.ui.tableMeta.setItem(i, 1, QTableWidgetItem(v_str))
        self.ui.tableMeta.resizeColumnToContents(0)

    def collect_metadata(self, folder: str) -> Dict[str, Any]:
        meta: Dict[str, Any] = {"目录": folder}
        # 1) 常见的提示词 / 参数文件
        prompt_text = self._read_first_text([
            os.path.join(folder, name) for name in (
                "prompt.txt", "prompts.txt", "neg_prompt.txt", "caption.txt"
            )
        ])
        if prompt_text:
            meta["提示词"] = prompt_text.strip()[:2000]

        # 2) 常见 JSON 参数/元数据
        json_data = self._read_first_json([
            os.path.join(folder, name) for name in (
                "metadata.json", "params.json", "info.json"
            )
        ])
        if json_data:
            # 直接解析常用键
            model = json_data.get("model") or json_data.get("model_name") or json_data.get("ckpt")
            if model:
                meta["模型名称"] = model
            # 如果 JSON 本身就包含 prompt，也补上
            if "prompt" in json_data and "提示词" not in meta:
                meta["提示词"] = str(json_data.get("prompt"))[:2000]
            meta["其他参数"] = json_data

        # 3) 视频文件列表
        videos = self._list_files(folder, exts={".mp4", ".mov", ".avi", ".mkv", ".webm"})
        if videos:
            meta["视频文件"] = ", ".join(os.path.basename(v) for v in videos[:20]) + (" ..." if len(videos) > 20 else "")

        # 4) 参考图（文件名包含 ref/reference，或在 ref/ 子目录）
        refs = []
        images = self._list_files(folder, exts={".png", ".jpg", ".jpeg", ".bmp", ".gif"})
        for p in images:
            name = os.path.basename(p).lower()
            if ("ref" in name) or ("reference" in name):
                refs.append(p)
        ref_dir = os.path.join(folder, "ref")
        if os.path.isdir(ref_dir):
            refs.extend(self._list_files(ref_dir, exts={".png", ".jpg", ".jpeg", ".bmp", ".gif"}))
        if refs:
            meta["参考图"] = ", ".join(os.path.basename(r) for r in refs[:20]) + (" ..." if len(refs) > 20 else "")

        return meta

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
        out: List[str] = []
        try:
            for name in os.listdir(folder):
                p = os.path.join(folder, name)
                if os.path.isfile(p):
                    _, ext = os.path.splitext(name)
                    if ext.lower() in exts:
                        out.append(p)
        except Exception:
            pass
        return out

    def on_reference_clicked(self):
        # 检查当前目录下是否有 “参考图” 的子目录
        current_path = self.ui.lineAddress.text().strip()
        ref_dir = os.path.join(current_path, "参考图")
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
        current_path = self.ui.lineAddress.text().strip()
        seq_dir = os.path.join(current_path, "序列帧")
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
        current_path = self.ui.lineAddress.text().strip()
        spine_dir = os.path.join(current_path, "Spine")
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
        current_path = self.ui.lineAddress.text().strip()
        video_dir = os.path.join(current_path, "视频")
        if os.path.isdir(video_dir):
            self.navigate_to_path(video_dir)
        else:
            try:
                os.makedirs(video_dir, exist_ok=True)
                self.navigate_to_path(video_dir)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法创建视频目录：\n{str(e)}", QMessageBox.Ok)
                