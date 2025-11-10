import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QComboBox, QMessageBox, QWidget, QToolTip
from PySide6.QtCore import Signal
from MuseLog.config_paths import get_config_file
from MuseLog.ui.ui_widget_video_detail import Ui_Form


REFERENCE_HISTORY_NAME = "video_detail_reference_history.json"
CONFIG_FILE = get_config_file(REFERENCE_HISTORY_NAME)
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
        self._setup_reference_model()

        self.ui.textEdit.textChanged.connect(self._on_prompt_changed)
        self.ui.saveButton.clicked.connect(self._on_save_clicked)
        self.ui.cancelButton.clicked.connect(self._on_cancel_clicked)
        self.ui.closeButton.clicked.connect(self._on_notify_close)
        self.ui.playButton.clicked.connect(self._on_play_video_clicked)
        self.ui.btnCopyCfg.clicked.connect(self._on_copy_cfg_clicked)
        self.ui.btnPasteCfg.clicked.connect(self._on_paste_cfg_clicked)

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

    def _setup_reference_model(self) -> None:
        model_list = [
            "未选择",
            "Doubao-Seedance-1.0-pro-fast 251015",
            "Doubao-Seedance-1.0-pro-250528",
            "即梦 视频 3.0 Pro Fast",
            "即梦 视频 3.0 Pro",
            "即梦 视频 3.0",
            "即梦 Agent",
            "wan2.2 i2v",
            "豆包"
        ]
        self.ui.comboRefModel.addItems(model_list)

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
        entry.setdefault("model", "未选择")

        self._initial_entry = deepcopy(entry)
        self._apply_metadata(entry)

    # ---------------------- UI 操作 ----------------------
    def _on_save_clicked(self) -> None:
        if not self._video_path or not self._metadata_path or not self._metadata_key:
            return
        prompt = self.ui.textEdit.toPlainText().strip()
        reference = self._reference_combo.currentText().strip()
        model = self.ui.comboRefModel.currentText().strip()
        qualified = self.ui.checkQualified.isChecked()

        entry = deepcopy(self._all_metadata.get(self._metadata_key, {}))
        if not isinstance(entry, dict):
            entry = {}

        entry.update({
            "video_path": self._video_path,
            "prompt": prompt,
            "model": model,
            "qualified": str(qualified),
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

    def _on_play_video_clicked(self) -> None:
        if not self._video_path or not os.path.isfile(self._video_path):
            QMessageBox.warning(self, "播放失败", "视频文件不存在，无法播放。", QMessageBox.Ok)
            return
        try:
            if os.name == 'nt':  # Windows
                os.startfile(self._video_path)
            elif os.name == 'posix':  # macOS or Linux
                import subprocess
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, self._video_path])
            else:
                QMessageBox.warning(self, "播放失败", "当前操作系统不支持自动播放视频。", QMessageBox.Ok)
        except Exception as exc:
            QMessageBox.critical(self, "播放失败", f"无法打开视频文件：\n{exc}")

    def _on_copy_cfg_clicked(self) -> None:
        if not self._video_path or not os.path.isfile(self._video_path):
            QMessageBox.warning(self, "复制失败", "视频文件不存在，无法复制配置。", QMessageBox.Ok)
            return
        prompt = self.ui.textEdit.toPlainText().strip()
        reference = self._reference_combo.currentText().strip()
        model = self.ui.comboRefModel.currentText().strip()
        qualified = self.ui.checkQualified.isChecked()

        cfg_lines = [
            f"视频路径: {self._video_path}",
            f"提示词: {prompt}",
            f"参考图: {reference or '无'}",
            f"模型: {model}",
            f"合格: {'是' if qualified else '否'}"
        ]
        cfg_text = "\n".join(cfg_lines)

        clipboard = QApplication.instance().clipboard()
        clipboard.setText(cfg_text)
        QToolTip.showText(self.ui.btnCopyCfg.mapToGlobal(self.ui.btnCopyCfg.rect().center()), "配置已复制到剪贴板。", self.ui.btnCopyCfg, self.ui.btnCopyCfg.rect(), 2000)

    def _on_paste_cfg_clicked(self) -> None:
        clipboard = QApplication.instance().clipboard()
        cfg_text = clipboard.text().strip()
        if not cfg_text:
            QMessageBox.warning(self, "粘贴失败", "剪贴板中没有可用的配置内容。", QMessageBox.Ok)
            return

        lines = cfg_text.splitlines()
        prompt = ""
        reference = ""
        model = "未选择"
        qualified = False

        for line in lines:
            if line.startswith("提示词:"):
                prompt = line[len("提示词:"):].strip()
            elif line.startswith("参考图:"):
                reference = line[len("参考图:"):].strip()
            elif line.startswith("模型:"):
                model = line[len("模型:"):].strip()
            elif line.startswith("合格:"):
                qualified_str = line[len("合格:"):].strip().lower()
                qualified = qualified_str in ("是", "true", "1", "yes")

        self.ui.textEdit.setPlainText(prompt)
        self._reference_combo.setCurrentText(reference)
        self.ui.comboRefModel.setCurrentText(model)
        self.ui.checkQualified.setChecked(qualified)
        QToolTip.showText(self.ui.btnPasteCfg.mapToGlobal(self.ui.btnPasteCfg.rect().center()), "配置已从剪贴板粘贴。", self.ui.btnPasteCfg, self.ui.btnPasteCfg.rect(), 2000)

    # ---------------------- 元数据维护 ----------------------

    def _default_metadata_path(self, video_path: str) -> str:
        folder = os.path.dirname(video_path)
        return os.path.join(folder, "提示词.txt")

    def _load_all_metadata(self) -> Dict[str, Dict[str, Any]]:
        self._reference_history = self._load_reference_history()

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

    def _load_reference_history(self) -> List[str]:
        history_file = Path(CONFIG_FILE)
        if not history_file.is_file():
            return []
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                payload = json.load(f)
            history = payload.get("history", [])
            if isinstance(history, list):
                return self._normalize_reference_history(history)
        except Exception as exc:
            print(f"[VideoDetailWidget] 参考图历史读取失败: {exc}")
        return []

    def _write_all_metadata(self, data: Dict[str, Dict[str, Any]]) -> None:
        self._write_reference_history()
        os.makedirs(os.path.dirname(self._metadata_path), exist_ok=True)
        payload: Dict[str, Any] = {key: value for key, value in data.items()}
        with open(self._metadata_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def _write_reference_history(self) -> None:
        history_file = Path(CONFIG_FILE)
        payload = {"history": self._reference_history}
        try:
            os.makedirs(history_file.parent, exist_ok=True)
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception as exc:
            print(f"[VideoDetailWidget] 参考图历史写入失败: {exc}")

    def _apply_metadata(self, metadata: Dict[str, Any]) -> None:
        prompt = metadata.get("prompt") or ""
        reference = metadata.get("reference") or ""
        model = metadata.get("model") or "未选择"
        qualified_str = metadata.get("qualified") or "False"
        qualified = qualified_str.lower() in ("1", "true", "yes")
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
        self.ui.comboRefModel.setCurrentText(model)
        self.ui.checkQualified.setChecked(qualified)
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
