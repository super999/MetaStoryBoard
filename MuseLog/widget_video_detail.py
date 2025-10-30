import json
import os
from typing import Any, Dict, Optional

from PySide6.QtWidgets import QWidget, QMessageBox

from MuseLog.ui.ui_widget_video_detail import Ui_Form


class VideoDetailWidget(QWidget):
    """使用 Designer 生成的 UI 展示并编辑视频元数据。"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self._video_path: Optional[str] = None
        self._metadata_path: Optional[str] = None
        self._initial_metadata: Dict[str, Any] = {}
        self._default_label_text = self.ui.label.text()
        self._default_label_style = self.ui.label.styleSheet()

        self.ui.textEdit.setAcceptRichText(False)
        self.ui.textEdit.setPlaceholderText("填写或查看该视频的提示词内容")
        self.ui.lineEdit.setPlaceholderText("可选：参考图路径或链接")
        self.ui.lineEdit.setClearButtonEnabled(True)

        self.ui.saveButton.clicked.connect(self._on_save_clicked)
        self.ui.cancelButton.clicked.connect(self._on_cancel_clicked)

        self._set_buttons_enabled(False)

    # ---------------------- 对外接口 ----------------------
    def set_video(self, video_path: str) -> None:
        """绑定视频文件，读取并展示其关联元数据。"""
        video_path = os.path.abspath(video_path)
        self._video_path = video_path
        self._metadata_path = self._default_metadata_path(video_path)

        if not os.path.isfile(video_path):
            self._set_buttons_enabled(False)
            self._show_error(f"视频文件不存在：{video_path}")
            self._initial_metadata = {}
            self._apply_metadata({})
            return

        self._show_error("")
        self._set_buttons_enabled(True)

        video_name = os.path.basename(video_path)
        self.ui.label.setText(f"提示词 - {video_name}")

        metadata = self._load_metadata()
        self._initial_metadata = metadata
        self._apply_metadata(metadata)

        reference = metadata.get("reference")
        if reference:
            self.ui.label_2.setText(f"参考图（当前：{os.path.basename(reference)}）")
        else:
            self.ui.label_2.setText("参考图")

    # ---------------------- UI 操作 ----------------------
    def _on_save_clicked(self) -> None:
        if not self._video_path or not self._metadata_path:
            return

        metadata = {
            "prompt": self.ui.textEdit.toPlainText().strip(),
            "reference": self.ui.lineEdit.text().strip(),
            "video": {
                "path": self._video_path,
            },
        }

        try:
            with open(self._metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            self._initial_metadata = metadata
            QMessageBox.information(self, "保存成功", f"元数据已写入：\n{self._metadata_path}")
        except Exception as exc:
            QMessageBox.critical(self, "保存失败", f"写入元数据文件时出错：\n{exc}")

    def _on_cancel_clicked(self) -> None:
        self._apply_metadata(self._initial_metadata)

    # ---------------------- 元数据维护 ----------------------
    def _default_metadata_path(self, video_path: str) -> str:
        stem, _ = os.path.splitext(video_path)
        return f"{stem}.meta.json"

    def _load_metadata(self) -> Dict[str, Any]:
        if not self._metadata_path or not os.path.isfile(self._metadata_path):
            return self._build_default_metadata()
        try:
            with open(self._metadata_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
        return self._build_default_metadata()

    def _build_default_metadata(self) -> Dict[str, Any]:
        meta: Dict[str, Any] = {
            "prompt": "",
            "reference": "",
        }
        if self._video_path and os.path.isfile(self._video_path):
            meta["video"] = {
                "path": self._video_path,
                "size": os.path.getsize(self._video_path),
            }
        return meta

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

    def _show_error(self, message: str) -> None:
        if message:
            self.ui.label.setText(message)
            self.ui.label.setStyleSheet("color: #d32f2f; font-weight: 600;")
        else:
            self.ui.label.setStyleSheet(self._default_label_style)
            self.ui.label.setText(self._default_label_text)
