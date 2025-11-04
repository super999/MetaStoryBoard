import os
import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QFileDialog,
)

from MuseLog.ui.ui_tab_video_gen_ai import Ui_TabVideoGenerateByAI

class TabVideoGenAIWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_TabVideoGenerateByAI()
        self.ui.setupUi(self)
        
        self.ui.btnRefImagePath.clicked.connect(self.on_ref_image_path_clicked)
        self.ui.btnCommit.clicked.connect(self.on_commit_clicked)
        
        # 加载默认路径
        self.load_default_paths()
        # self.load_reference_image()
    
    # 界面加载完成后调用
    def showEvent(self, event):
        super().showEvent(event)
        self.load_reference_image()
        
    def on_commit_clicked(self):
        self.save_default_paths()

    def on_ref_image_path_clicked(self):
        file_path = QFileDialog.getOpenFileName(self, "选择参考图片", "", "图片文件 (*.png *.jpg *.jpeg)")[0]
        if file_path:
            self.ui.lineRefImagePath.setText(file_path)       
        else:
            self.ui.lineRefImagePath.setText("未选择参考图片")  
        self.load_reference_image()
        self.save_default_paths()
    
    def load_default_paths(self):
        path = "video_gen_default_path.json"
        default_ref_image_path = "未选择参考图片"
        default_prompt_text = "未输入提示词"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                import json
                data = json.load(f)
                ref_image_path = data.get("ref_image_path", "")
                self.ui.lineRefImagePath.setText(ref_image_path)
                prompt_text = data.get("prompt_text", "")
                self.ui.textPrompt.setPlainText(prompt_text)
        

    def save_default_paths(self):
        ref_path = self.ui.lineRefImagePath.text().strip()
        if not ref_path:
            return
        prompt_text = self.ui.textPrompt.toPlainText().strip()
        if not prompt_text:
            return
        
        path = "video_gen_default_path.json"
        data = {
            "ref_image_path": ref_path,
            "prompt_text": prompt_text
        }
        with open(path, "w", encoding="utf-8") as f:

            json.dump(data, f, ensure_ascii=False, indent=4)
    
    def load_reference_image(self):
        ref_image_path = self.ui.lineRefImagePath.text().strip()
        if not ref_image_path:
            self.ui.labelRefImagePreview.setText("未选择参考图片")
            return
        if os.path.exists(ref_image_path):
            pixmap = QPixmap(ref_image_path)
            scaled_pixmap = pixmap.scaled(self.ui.labelRefImagePreview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.ui.labelRefImagePreview.setPixmap(scaled_pixmap)
        else:
            self.ui.labelRefImagePreview.setText("未选择参考图片")