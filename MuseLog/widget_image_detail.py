import os
import os
from typing import Optional
import subprocess
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMessageBox, QWidget, QToolTip

from PySide6.QtCore import Qt, Signal
from MuseLog.ui.ui_widget_image_detail import Ui_Form
from PySide6.QtGui import QPixmap, QResizeEvent
from MuseLog.GTools.image_processor import ImageProcessor


class WidgetImageDetail(QWidget):
    # pySignals
    notify_close = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self._image_processor = ImageProcessor()
        self.image_path: Optional[str] = None
        self._original_pixmap: Optional[QPixmap] = None
        self.ui.labelImageRect.setAlignment(Qt.AlignCenter)
        self.ui.labelImageRect.setScaledContents(False)
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

    def bind_events(self) -> None:
        self.ui.btnCopyPath.clicked.connect(self.on_copy_path_clicked)
        self.ui.btnRemBG.clicked.connect(self.on_remove_background_clicked)
        self.ui.btnExplorer.clicked.connect(self.on_explore_clicked)

    def on_explore_clicked(self) -> None:
        if not self.image_path:
            QMessageBox.warning(self, "警告", "没有可浏览的图片。", QMessageBox.Ok)
            return
        folder = os.path.dirname(self.image_path)
        # 使用系统文件管理器打开文件夹并选中图片
        if os.name == 'nt':  # Windows
            subprocess.run(['explorer', '/select,', self.image_path])
        elif os.name == 'posix':  # macOS or Linux
            try:
                if sys.platform == 'darwin':  # macOS
                    subprocess.run(['open', '-R', self.image_path])
                else:  # Linux
                    subprocess.run(['xdg-open', folder])
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法打开文件夹：\n{e}", QMessageBox.Ok)


    def on_remove_background_clicked(self) -> None:
        if not self.image_path:
            QMessageBox.warning(self, "警告", "没有可处理的图片。", QMessageBox.Ok)
            return
        base_name = os.path.basename(self.image_path)
        target_name = f"{base_name}_扣除背景.png"
        target_path = os.path.join(os.path.dirname(self.image_path), target_name)
        self._image_processor.remove_background(self.image_path, target_path)
        QMessageBox.information(self, "完成", f"图片背景已去除，保存为: {target_name}", QMessageBox.Ok)

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