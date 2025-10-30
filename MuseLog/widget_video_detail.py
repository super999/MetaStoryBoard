import json
import os
from copy import deepcopy
from typing import Any, Dict, Optional

from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import Signal
from MuseLog.ui.ui_widget_video_detail import Ui_Form


class VideoDetailWidget(QWidget):
    """使用 Designer 生成的 UI 展示并编辑视频元数据。"""
    # pySignals
    notify_close = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self._video_path: Optional[str] = None
        self._metadata_path: Optional[str] = None
        self._metadata_key: Optional[str] = None
        self._all_metadata: Dict[str, Dict[str, Any]] = {}
        self._initial_entry: Dict[str, Any] = {}

        self._default_label_text = self.ui.label.text()
        self._default_label_style = self.ui.label.styleSheet()

        self.ui.textEdit.setAcceptRichText(False)
        self.ui.textEdit.setPlaceholderText("填写或查看该视频的提示词内容")
        self.ui.lineEdit.setPlaceholderText("可选：参考图路径或链接")
        self.ui.lineEdit.setClearButtonEnabled(True)

        self.ui.saveButton.clicked.connect(self._on_save_clicked)
        self.ui.cancelButton.clicked.connect(self._on_cancel_clicked)
        self.ui.closeButton.clicked.connect(self._on_notify_close)

        self._set_buttons_enabled(False)

    # ---------------------- 对外接口 ----------------------
    def set_video(self, video_path: str) -> None:
        """绑定视频文件，读取并展示其关联元数据。"""
        video_path = os.path.abspath(video_path)
        self._video_path = video_path
        self._metadata_path = self._default_metadata_path(video_path)
        self._metadata_key = os.path.basename(video_path)

        if not os.path.isfile(video_path):
            self._set_buttons_enabled(False)
            self._show_error(f"视频文件不存在：{video_path}")
            self._initial_entry = {}
            self._apply_metadata({})
            self._update_reference_label("")
            return

        self._show_error("")
        self._set_buttons_enabled(True)

        video_name = self._metadata_key or os.path.basename(video_path)
        self.ui.label.setText(f"提示词 - {video_name}")

        # 加载元数据
        all_metadata = self._load_all_metadata()
        self._all_metadata = all_metadata
        entry = deepcopy(all_metadata.get(video_name, {}))
        if not isinstance(entry, dict):
            entry = {"prompt": str(entry)} if entry is not None else {}

        entry.setdefault("video_path", self._video_path)

        self._initial_entry = deepcopy(entry)
        self._apply_metadata(entry)
        self._update_reference_label(entry.get("reference"))

    # ---------------------- UI 操作 ----------------------
    def _on_save_clicked(self) -> None:
        if not self._video_path or not self._metadata_path or not self._metadata_key:
            return
        prompt = self.ui.textEdit.toPlainText().strip()
        reference = self.ui.lineEdit.text().strip()

        entry = deepcopy(self._all_metadata.get(self._metadata_key, {}))
        if not isinstance(entry, dict):
            entry = {}

        entry.update({
            "video_path": self._video_path,
            "prompt": prompt,
            "reference": reference,
        })

        self._all_metadata[self._metadata_key] = entry

        try:
            self._write_all_metadata(self._all_metadata)
            self._initial_entry = deepcopy(entry)
            self._apply_metadata(entry)
            self._update_reference_label(reference)
            QMessageBox.information(self, "保存成功", f"元数据已写入：\n{self._metadata_path}")
        except Exception as exc:
            QMessageBox.critical(self, "保存失败", f"写入元数据文件时出错：\n{exc}")

    def _on_cancel_clicked(self) -> None:
        self._apply_metadata(self._initial_entry)
        self._update_reference_label(self._initial_entry.get("reference"))

    def _on_notify_close(self) -> None:
        self.notify_close.emit()
    
    # ---------------------- 元数据维护 ----------------------
    def _default_metadata_path(self, video_path: str) -> str:
        folder = os.path.dirname(video_path)
        return os.path.join(folder, "提示词.txt")

    def _load_all_metadata(self) -> Dict[str, Dict[str, Any]]:
        if not self._metadata_path or not os.path.isfile(self._metadata_path):
            return {}

        try:
            with open(self._metadata_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:
            print(f"[VideoDetailWidget] 元数据读取失败: {exc}")
            return {}

        if not isinstance(data, dict):
            return {}

        normalized: Dict[str, Dict[str, Any]] = {}
        for key, value in data.items():
            if isinstance(value, dict):
                normalized[key] = value
            elif value is None:
                normalized[key] = {}
            else:
                normalized[key] = {"prompt": str(value)}

        return normalized

    def _write_all_metadata(self, data: Dict[str, Dict[str, Any]]) -> None:
        os.makedirs(os.path.dirname(self._metadata_path), exist_ok=True)
        with open(self._metadata_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _apply_metadata(self, metadata: Dict[str, Any]) -> None:
        prompt = metadata.get("prompt") or ""
        reference = metadata.get("reference") or ""
        self.ui.textEdit.blockSignals(True)
        self.ui.lineEdit.blockSignals(True)
        self.ui.textEdit.setPlainText(prompt)
        self.ui.lineEdit.setText(reference)
        self.ui.textEdit.blockSignals(False)
        self.ui.lineEdit.blockSignals(False)

    # ---------------------- 辅助方法 ----------------------
    def _set_buttons_enabled(self, enabled: bool) -> None:
        self.ui.saveButton.setEnabled(enabled)
        self.ui.cancelButton.setEnabled(enabled)

    def _update_reference_label(self, reference: Optional[str]) -> None:
        if reference:
            self.ui.label_2.setText(f"参考图（当前：{os.path.basename(reference)}）")
        else:
            self.ui.label_2.setText("参考图")

    def _show_error(self, message: str) -> None:
        if message:
            self.ui.label.setText(message)
            self.ui.label.setStyleSheet("color: #d32f2f; font-weight: 600;")
        else:
            self.ui.label.setStyleSheet(self._default_label_style)
            self.ui.label.setText(self._default_label_text)
