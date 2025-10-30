import json
import os
from copy import deepcopy
from typing import Any, Dict, List, Optional

from PySide6.QtWidgets import QComboBox, QMessageBox, QWidget
from PySide6.QtCore import Signal
from MuseLog.ui.ui_widget_video_detail import Ui_Form


REFERENCE_HISTORY_KEY = "__reference_history__"
REFERENCE_HISTORY_LIMIT = 20
REFERENCE_PLACEHOLDER = "可选：参考图路径或链接"


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
        self._reference_history: List[str] = []

        self._default_label_text = self.ui.label.text()
        self._default_label_style = self.ui.label.styleSheet()
        self._current_label_title = self._default_label_text
        self._default_reference_label = self.ui.label_2.text()
        self._dirty = False
        self._error_active = False

        self.ui.textEdit.setAcceptRichText(False)
        self.ui.textEdit.setPlaceholderText("填写或查看该视频的提示词内容")

        self._reference_combo: QComboBox = self._setup_reference_combo()

        self.ui.textEdit.textChanged.connect(self._on_prompt_changed)
        self.ui.saveButton.clicked.connect(self._on_save_clicked)
        self.ui.cancelButton.clicked.connect(self._on_cancel_clicked)
        self.ui.closeButton.clicked.connect(self._on_notify_close)

        self._set_buttons_enabled(False)

    def _setup_reference_combo(self) -> QComboBox:
        original = self.ui.lineEdit
        placeholder = getattr(original, "placeholderText", lambda: "")()
        size_policy = original.sizePolicy()

        combo = QComboBox(self)
        combo.setObjectName("referenceCombo")
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        combo.setDuplicatesEnabled(False)
        combo.setMinimumSize(original.minimumSize())
        combo.setMaximumSize(original.maximumSize())
        combo.setSizePolicy(size_policy)
        combo.setMaxVisibleItems(REFERENCE_HISTORY_LIMIT)

        layout = self.ui.verticalLayout
        index = layout.indexOf(original)
        layout.insertWidget(index, combo)
        layout.removeWidget(original)
        original.deleteLater()

        line_edit = combo.lineEdit()
        if line_edit is not None:
            line_edit.setPlaceholderText(placeholder or REFERENCE_PLACEHOLDER)
            line_edit.setClearButtonEnabled(True)
            line_edit.textEdited.connect(self._on_reference_text_edited)

        combo.activated.connect(self._on_reference_activated)

        setattr(self.ui, "referenceCombo", combo)
        setattr(self.ui, "lineEdit", None)

        return combo

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
            self._current_label_title = self._default_label_text
            self._dirty = False
            self._reference_history = []
            self._initial_entry = {}
            self._apply_metadata({})
            return

        video_name = self._metadata_key or os.path.basename(video_path)
        self._current_label_title = f"提示词 - {video_name}"
        self._show_error("")
        self._set_buttons_enabled(True)

        # 加载元数据
        all_metadata = self._load_all_metadata()
        self._all_metadata = all_metadata
        entry = deepcopy(all_metadata.get(video_name, {}))
        if not isinstance(entry, dict):
            entry = {"prompt": str(entry)} if entry is not None else {}

        entry.setdefault("video_path", self._video_path)

        self._initial_entry = deepcopy(entry)
        self._apply_metadata(entry)

    # ---------------------- UI 操作 ----------------------
    def _on_save_clicked(self) -> None:
        if not self._video_path or not self._metadata_path or not self._metadata_key:
            return
        prompt = self.ui.textEdit.toPlainText().strip()
        reference = self._reference_combo.currentText().strip()

        entry = deepcopy(self._all_metadata.get(self._metadata_key, {}))
        if not isinstance(entry, dict):
            entry = {}

        entry.update({
            "video_path": self._video_path,
            "prompt": prompt,
        })

        if reference:
            entry["reference"] = reference
        else:
            entry.pop("reference", None)

        self._update_reference_history(reference)

        self._all_metadata[self._metadata_key] = entry

        try:
            self._write_all_metadata(self._all_metadata)
            self._initial_entry = deepcopy(entry)
            self._apply_metadata(entry)
            QMessageBox.information(self, "保存成功", f"元数据已写入：\n{self._metadata_path}")
        except Exception as exc:
            QMessageBox.critical(self, "保存失败", f"写入元数据文件时出错：\n{exc}")

    def _on_cancel_clicked(self) -> None:
        self._apply_metadata(self._initial_entry)

    def _on_notify_close(self) -> None:
        self.notify_close.emit()
    
    # ---------------------- 元数据维护 ----------------------
    def _default_metadata_path(self, video_path: str) -> str:
        folder = os.path.dirname(video_path)
        return os.path.join(folder, "提示词.txt")

    def _load_all_metadata(self) -> Dict[str, Dict[str, Any]]:
        if not self._metadata_path or not os.path.isfile(self._metadata_path):
            self._reference_history = []
            return {}

        try:
            with open(self._metadata_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:
            print(f"[VideoDetailWidget] 元数据读取失败: {exc}")
            self._reference_history = []
            return {}

        if not isinstance(data, dict):
            self._reference_history = []
            return {}

        normalized: Dict[str, Dict[str, Any]] = {}
        for key, value in data.items():
            if key == REFERENCE_HISTORY_KEY:
                self._reference_history = self._normalize_reference_history(value)
                continue
            if isinstance(value, dict):
                normalized[key] = value
            elif value is None:
                normalized[key] = {}
            else:
                normalized[key] = {"prompt": str(value)}

        return normalized

    def _write_all_metadata(self, data: Dict[str, Dict[str, Any]]) -> None:
        os.makedirs(os.path.dirname(self._metadata_path), exist_ok=True)
        payload: Dict[str, Any] = {key: value for key, value in data.items()}
        if self._reference_history:
            payload[REFERENCE_HISTORY_KEY] = self._reference_history
        else:
            payload.pop(REFERENCE_HISTORY_KEY, None)
        with open(self._metadata_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def _apply_metadata(self, metadata: Dict[str, Any]) -> None:
        prompt = metadata.get("prompt") or ""
        reference = metadata.get("reference") or ""
        self.ui.textEdit.blockSignals(True)
        self._reference_combo.blockSignals(True)
        reference_line = self._reference_combo.lineEdit()
        if reference_line is not None:
            reference_line.blockSignals(True)

        self.ui.textEdit.setPlainText(prompt)
        self._populate_reference_history(reference)

        if reference_line is not None:
            reference_line.blockSignals(False)
        self._reference_combo.blockSignals(False)
        self.ui.textEdit.blockSignals(False)

        self._update_reference_label(reference)
        self._dirty = False
        self._refresh_title()

    # ---------------------- 辅助方法 ----------------------
    def _normalize_reference_history(self, value: Any) -> List[str]:
        if not isinstance(value, list):
            return []
        history: List[str] = []
        for item in value:
            text = str(item).strip()
            if text and text not in history:
                history.append(text)
            if len(history) >= REFERENCE_HISTORY_LIMIT:
                break
        return history

    def _update_reference_history(self, reference: str) -> None:
        text = reference.strip()
        if not text:
            return
        history = [item for item in self._reference_history if item != text]
        history.insert(0, text)
        self._reference_history = history[:REFERENCE_HISTORY_LIMIT]

    def _populate_reference_history(self, current_reference: Optional[str]) -> None:
        text = (current_reference or "").strip()
        combo = self._reference_combo
        combo.blockSignals(True)
        line_edit = combo.lineEdit()
        if line_edit is not None:
            line_edit.blockSignals(True)

        items: List[str] = []
        if text:
            items.append(text)
        for item in self._reference_history:
            if item and item not in items:
                items.append(item)

        combo.clear()
        if items:
            combo.addItems(items)
        combo.setCurrentText(text)

        if line_edit is not None:
            line_edit.blockSignals(False)
        combo.blockSignals(False)

    def _set_buttons_enabled(self, enabled: bool) -> None:
        self.ui.saveButton.setEnabled(enabled)
        self.ui.cancelButton.setEnabled(enabled)
        self.ui.textEdit.setEnabled(enabled)
        self._reference_combo.setEnabled(enabled)

    def _update_reference_label(self, reference: Optional[str]) -> None:
        ref_text = (reference or "").strip()
        if ref_text:
            self.ui.label_2.setText(f"参考图（当前：{os.path.basename(ref_text)}）")
        else:
            self.ui.label_2.setText(self._default_reference_label)

    def _show_error(self, message: str) -> None:
        self._error_active = bool(message)
        if self._error_active:
            self.ui.label.setText(message)
            self.ui.label.setStyleSheet("color: #d32f2f; font-weight: 600;")
        else:
            self.ui.label.setStyleSheet(self._default_label_style)
            self._refresh_title()

    def _on_prompt_changed(self) -> None:
        self._mark_dirty()

    def _on_reference_text_edited(self, text: str) -> None:
        self._update_reference_label(text)
        self._mark_dirty()

    def _on_reference_activated(self, index: int) -> None:
        text = self._reference_combo.itemText(index)
        self._update_reference_label(text)
        self._mark_dirty()

    def _mark_dirty(self) -> None:
        if not self._dirty:
            self._dirty = True
            if not self._error_active:
                self._refresh_title()

    def _refresh_title(self) -> None:
        if self._error_active:
            return
        title = self._current_label_title or self._default_label_text
        self.ui.label.setStyleSheet(self._default_label_style)
        if self._dirty:
            self.ui.label.setText(f"{title} *未保存")
        else:
            self.ui.label.setText(title)
