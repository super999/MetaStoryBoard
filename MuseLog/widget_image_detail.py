from copy import deepcopy
import os
from pathlib import Path
import subprocess
import sys
import json
import logging
from typing import Any, Dict, Optional

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMessageBox, QWidget, QToolTip

from PySide6.QtCore import Qt, Signal
from MuseLog.config_paths import get_config_file
from MuseLog.explorer_custom_widgets import _resolve_tab_id
from MuseLog.ui.ui_widget_image_detail import Ui_Form
from PySide6.QtGui import QPixmap, QResizeEvent
from MuseLog.GTools.image_processor import ImageProcessor
from MuseLog.explorer_signals import signal_manager

REFERENCE_HISTORY_NAME = "image_detail_reference_history.json"
CONFIG_FILE = get_config_file(REFERENCE_HISTORY_NAME)
REFERENCE_HISTORY_LIMIT = 20
REFERENCE_PLACEHOLDER = "可选：参考图路径或链接"

class WidgetImageDetail(QWidget):
    # pySignals
    notify_close = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self._image_processor = ImageProcessor()
        self.image_path: Optional[str] = None
        self._metadata_path: Optional[str] = None
        self._metadata_key: Optional[str] = None
        self.all_metadata: Dict[str, Any] = {}
        self._initial_entry: Dict[str, Any] = {}
        self._dirty: bool = False
        self._original_pixmap: Optional[QPixmap] = None
        self.ui.labelImageRect.setAlignment(Qt.AlignCenter)
        self.ui.labelImageRect.setScaledContents(False)
        self._setup_reference_model()
        self.bind_events()

    def set_image(self, image_path: str) -> None:
        self.image_path = image_path
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            self._original_pixmap = None
            self.ui.labelImageRect.setText("无法加载图片")
            return
        self._original_pixmap = pixmap
        self._update_image_display()
        image_name = os.path.basename(image_path)
        self._metadata_key = image_name
        self._metadata_path = self._default_metadata_path(image_path)
        self.all_metadata = self._load_all_metadata()
        entry = deepcopy(self.all_metadata.get(image_name, {}))        
        self._initial_entry = deepcopy(entry)
        self._app_metadata(entry)

    def bind_events(self) -> None:
        self.ui.btnCopyPath.clicked.connect(self.on_copy_path_clicked)
        self.ui.btnRemBG.clicked.connect(self.on_remove_background_clicked)
        self.ui.btnExplorer.clicked.connect(self.on_explore_clicked)
        self.ui.btnSave.clicked.connect(self.on_save_clicked)
        self.ui.btnCopyCfg.clicked.connect(self.on_copy_config_clicked)
        self.ui.btnPasteCfg.clicked.connect(self.on_paste_config_clicked)

    def on_explore_clicked(self) -> None:
        if not self.image_path:
            QMessageBox.warning(self, "警告", "没有可浏览的图片。", QMessageBox.Ok)
            return
        target = os.path.abspath(self.image_path)
        if not os.path.exists(target):
            QMessageBox.warning(self, "警告", "图片文件不存在，无法打开所在位置。", QMessageBox.Ok)
            return

        try:
            if sys.platform.startswith("win"):
                # explorer /select,"path" 会选中目标文件
                subprocess.run(["explorer", "/select,", os.path.normpath(target)], check=False)
            elif sys.platform == "darwin":
                subprocess.run(["open", "-R", target], check=False)
            else:
                folder = os.path.dirname(target) or "."
                subprocess.run(["xdg-open", folder], check=False)
        except Exception as exc:
            QMessageBox.warning(self, "错误", f"无法打开文件夹：\n{exc}", QMessageBox.Ok)


    def on_remove_background_clicked(self) -> None:
        if not self.image_path:
            QMessageBox.warning(self, "警告", "没有可处理的图片。", QMessageBox.Ok)
            return
        base_name_without_ext = os.path.splitext(os.path.basename(self.image_path))[0]
        target_name = f"{base_name_without_ext}_扣除背景.png"
        target_path = os.path.join(os.path.dirname(self.image_path), target_name)
        self._image_processor.remove_background(self.image_path, target_path)
        QMessageBox.information(self, "完成", f"图片背景已去除，保存为: {target_name}", QMessageBox.Ok)
        tab_id = _resolve_tab_id(self)
        signal_manager.gui_fresh_tab_collect_metadata.emit(tab_id)

    def on_copy_path_clicked(self) -> None:
        if not self.image_path:
            QMessageBox.warning(self, "警告", "没有可复制的图片路径。", QMessageBox.Ok)
            return
        clipboard = QApplication.clipboard()
        clipboard.setText(self.image_path)
        QToolTip.showText(
            self.ui.btnCopyPath.mapToGlobal(self.ui.btnCopyPath.rect().topLeft()),
            "图片路径已复制到剪贴板。",
            self.ui.btnCopyPath,
            msecShowTime=2000,
        )

    def resizeEvent(self, event: QResizeEvent) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._update_image_display()

    def _update_image_display(self) -> None:
        if not self._original_pixmap:
            return
        target_size = self.ui.labelImageRect.size()
        if target_size.width() <= 0 or target_size.height() <= 0:
            return
        scaled = self._original_pixmap.scaled(
            target_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.ui.labelImageRect.setPixmap(scaled)
        
    def on_save_clicked(self) -> None:
        if not self.image_path or not self._metadata_path or not self._metadata_key:
            QMessageBox.warning(self, "警告", "没有可保存的图片元数据。", QMessageBox.Ok)
            return
        prompt = self.ui.textEdit.toPlainText().strip()
        reference_image = self.ui.comboRefImage.currentText().strip()
        model = self.ui.comboRefModel.currentText().strip()
        qulified = self.ui.checkQulified.isChecked()
        
        entry = deepcopy(self.all_metadata.get(self._metadata_key, {}))
        if not isinstance(entry, dict):
            entry = {}
        
        entry.update({
            "prompt": prompt,
            "reference_image": reference_image,
            "model": model,
            "qualified_str": str(qulified),
        })
        self.all_metadata[self._metadata_key] = entry

        try:
            self._write_all_metadata(self.all_metadata)
            self._initial_entry = deepcopy(entry)
            self._app_metadata(entry)
            QToolTip.showText(self.ui.btnSave.mapToGlobal(self.ui.btnSave.rect().topLeft()),
                "图片元数据已保存。",
                self.ui.btnSave,
                msecShowTime=2000,
            )
        except Exception as exc:
            QMessageBox.critical(self, "保存失败", f"写入元数据文件时出错：\n{exc}")

    model_list = [
            "Google-Whisk",
            "Google-ImageFx",
            "Google-Gemini3Pro",
            "Pinterest",
            "豆包",
            "ChatGPT",
            "Krita",
            "ComfyUI",            
        ]

    def _setup_reference_model(self) -> None:
        
        self.ui.comboRefModel.clear()
        self.ui.comboRefModel.addItems(self.model_list)
    
    def _default_metadata_path(self, image_path: str) -> str:
        folder = os.path.dirname(image_path)        
        return os.path.join(folder, f"提示词.json")
    
    def _load_all_metadata(self) -> dict:        
        if not self._metadata_path or not os.path.exists(self._metadata_path):
            return {}
        
        try:
            import json
            with open(self._metadata_path, "r", encoding="utf-8") as f:
                all_metadata = json.load(f)
        except Exception as exc:
            QMessageBox.warning(self, "错误", f"无法加载元数据文件：\n{exc}", QMessageBox.Ok)
            return {}
        
        if not isinstance(all_metadata, dict):
            return {}
        
        normalized = {}
        for key, value in all_metadata.items():
            if isinstance(value, dict):
                normalized[key] = value
            elif value is None:
                normalized[key] = {}
            else:
                normalized[key] = {"prompt": str(value)}
        return normalized

    def _app_metadata(self, metadata: Dict[str, Any]) -> None:
        prompt = metadata.get("prompt", "")
        reference_image = metadata.get("reference_image", "")
        model = metadata.get("model", "未选择")
        qualified_str = metadata.get("qualified_str", "False")
        qulified = qualified_str.lower() in ("true", "1", "yes", "是", "已合格")
        self.ui.textEdit.setPlainText(prompt)
        if reference_image:
            if reference_image not in [self.ui.comboRefImage.itemText(i) for i in range(self.ui.comboRefImage.count())]:
                self.ui.comboRefImage.addItem(reference_image)
            self.ui.comboRefImage.setCurrentText(reference_image)
        if model:
            if model not in self.model_list:
                self.model_list.append(model)
                self.ui.comboRefModel.addItem(model)
                self.model_list.append(model)
            self.ui.comboRefModel.setCurrentText(model)
        self.ui.checkQulified.setChecked(qulified)
        self._update_reference_label(reference_image)
    
    def _write_all_metadata(self, all_metadata: Dict[str, Any]) -> None:
        self._write_reference_history()
        os.makedirs(os.path.dirname(self._metadata_path), exist_ok=True)
        payload: Dict[str, Any] = { key: value for key, value in all_metadata.items() }
        with open(self._metadata_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=4)
            
    def _write_reference_history(self) -> None:
        history_path = Path(CONFIG_FILE)
        payload: Dict[str, Any] = { "history": [] }
        try:
            os.makedirs(history_path.parent, exist_ok=True)
            with open(history_path, "r", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception:
            logging.error("无法读取参考图历史配置文件，创建新的。")
    
    def _update_reference_label(self, reference_image: str) -> None:
        if reference_image:
            self.ui.label_4.setText(f"参考图（当前：{reference_image})")
        else:
            self.ui.label_4.setText("参考图: 无")
            
    def on_copy_config_clicked(self) -> None:
        if not self.image_path:
            QMessageBox.warning(self, "警告", "没有可复制配置的图片。", QMessageBox.Ok)
            return
        if not self._metadata_key or not self.all_metadata.get(self._metadata_key):
            QMessageBox.warning(self, "警告", "当前图片没有元数据，无法复制配置。", QMessageBox.Ok)
            return
        
        prompt = self.ui.textEdit.toPlainText().strip()
        reference_image = self.ui.comboRefImage.currentText().strip()
        model = self.ui.comboRefModel.currentText().strip()
        qulified = self.ui.checkQulified.isChecked()

        payload = {
            "prompt": prompt,
            "reference_image": reference_image,
            "model": model,
            "qualified": bool(qulified),
        }
        # 使用 JSON，保证 prompt 中的换行/特殊字符能完整保留。
        config_text = "MuseLogImageCfg/v1\n" + json.dumps(payload, ensure_ascii=False)

        clipboard = QApplication.clipboard()
        clipboard.setText(config_text)
        QToolTip.showText(
            self.ui.btnCopyCfg.mapToGlobal(self.ui.btnCopyCfg.rect().topLeft()),
            "图片元数据配置已复制到剪贴板。",
            self.ui.btnCopyCfg,
            msecShowTime=2000,
        )
        
    def on_paste_config_clicked(self) -> None:
        if not self.image_path:
            QMessageBox.warning(self, "警告", "没有可粘贴配置的图片。", QMessageBox.Ok)
            return
        clipboard = QApplication.clipboard()
        config_text = clipboard.text().strip()
        if not config_text:
            QMessageBox.warning(self, "警告", "剪贴板中没有可用的配置文本。", QMessageBox.Ok)
            return
        
        prompt = ""
        reference_image = ""
        model = ""
        qualified = False

        # 新格式：MuseLogImageCfg/v1 + JSON
        if config_text.startswith("MuseLogImageCfg/v1"):
            try:
                _, json_part = config_text.split("\n", 1)
                obj = json.loads(json_part)
                if isinstance(obj, dict):
                    prompt = str(obj.get("prompt", ""))
                    reference_image = str(obj.get("reference_image", ""))
                    model = str(obj.get("model", ""))
                    qualified = bool(obj.get("qualified", False))
            except Exception:
                QMessageBox.warning(self, "警告", "剪贴板配置解析失败（JSON 格式）。", QMessageBox.Ok)
                return
        else:
            # 旧格式兼容：按行解析，但 Prompt 允许多行（直到遇到下一个字段标题）
            def _is_header_line(s: str) -> bool:
                return (
                    s.startswith("Prompt:")
                    or s.startswith("Reference Image:")
                    or s.startswith("Model:")
                    or s.startswith("Qualified:")
                )

            current_key: Optional[str] = None
            prompt_lines = []
            lines = config_text.splitlines()
            for raw_line in lines:
                line = raw_line
                if line.startswith("Prompt:"):
                    current_key = "prompt"
                    prompt_lines = [line[len("Prompt:"):].lstrip()]
                elif line.startswith("Reference Image:"):
                    current_key = "reference_image"
                    reference_image = line[len("Reference Image:"):].strip()
                elif line.startswith("Model:"):
                    current_key = "model"
                    model = line[len("Model:"):].strip()
                elif line.startswith("Qualified:"):
                    current_key = "qualified"
                    qualified_str = line[len("Qualified:"):].strip()
                    qualified = qualified_str.lower() in ("true", "1", "yes", "y", "是", "已合格")
                else:
                    # 旧格式里只有 prompt 可能跨行；遇到其他非 header 行时，如果当前处于 prompt，继续拼接
                    if current_key == "prompt":
                        prompt_lines.append(raw_line)

            if prompt_lines:
                prompt = "\n".join(prompt_lines).strip()
                
        self.ui.textEdit.setPlainText(prompt)
        if reference_image:
            if reference_image not in [self.ui.comboRefImage.itemText(i) for i in range(self.ui.comboRefImage.count())]:
                self.ui.comboRefImage.addItem(reference_image)
            self.ui.comboRefImage.setCurrentText(reference_image)
        if model:
            if model not in self.model_list:
                self.model_list.append(model)
                self.ui.comboRefModel.addItem(model)
            self.ui.comboRefModel.setCurrentText(model)
        self.ui.checkQulified.setChecked(qualified)           
        
        QToolTip.showText(
            self.ui.btnPasteCfg.mapToGlobal(self.ui.btnPasteCfg.rect().topLeft()),
            "图片元数据配置已从剪贴板粘贴。",
            self.ui.btnPasteCfg,
            msecShowTime=2000,
        )