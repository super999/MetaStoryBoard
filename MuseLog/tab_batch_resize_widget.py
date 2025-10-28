import json
import os

from PySide6.QtWidgets import QWidget, QFileDialog, QMessageBox

from MuseLog.batch_resize_utils import BatchResizer
from MuseLog.ui.ui_tab_batch_resize import Ui_TabBatchResize


class TabBatchResizeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_TabBatchResize()
        self.ui.setupUi(self)
        # 绑定事件
        self.ui.btnSelectInputFolder.clicked.connect(self.select_input_folder)
        self.ui.btnSelectOutputFolder.clicked.connect(self.select_output_folder)
        self.ui.btnBatchResize.clicked.connect(self.batch_resize)
        self.ui.radioScale.toggled.connect(self.update_mode)
        self.ui.radioFixedWidth.toggled.connect(self.update_mode)
        self.ui.radioFixedHeight.toggled.connect(self.update_mode)
        self.ui.btnSavePath.clicked.connect(self.save_default_paths)
        self.ui.btnReloadImage.clicked.connect(lambda: self.load_images(self.ui.lineInputFolder.text().strip()))
        self.ui.btnClearList.clicked.connect(self.clear_list)
        self.ui.btnRemoveImages.clicked.connect(self.remove_images)  # 删除选中的图片
        self.update_mode()
        # 状态
        self.image_paths = []
        self.ui.labelStatus.setText("状态：等待操作")
        # 加载��认路径
        self.load_default_paths()

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择输入文件夹")
        if folder:
            self.ui.lineInputFolder.setText(folder)
            self.load_images(folder)
        else:
            self.ui.labelStatus.setText("未选择输入文件夹")

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if folder:
            self.ui.lineOutputFolder.setText(folder)
        else:
            self.ui.labelStatus.setText("未选择输出文件夹")

    def load_images(self, folder):
        self.image_paths = []
        self.ui.listImages.clear()
        for fname in os.listdir(folder):
            if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                path = os.path.join(folder, fname)
                self.image_paths.append(path)
                self.ui.listImages.addItem(path)
        self.ui.labelStatus.setText(f"已加载 {len(self.image_paths)} 张图片")

    def update_mode(self):
        # Enable inputs according to selected mode
        if self.ui.radioScale.isChecked():
            self.ui.spinScale.setEnabled(True)
            self.ui.spinWidth.setEnabled(False)
            self.ui.spinHeight.setEnabled(False)
        elif self.ui.radioFixedWidth.isChecked():
            self.ui.spinScale.setEnabled(False)
            self.ui.spinWidth.setEnabled(True)
            self.ui.spinHeight.setEnabled(False)
        else:  # fixed height
            self.ui.spinScale.setEnabled(False)
            self.ui.spinWidth.setEnabled(False)
            self.ui.spinHeight.setEnabled(True)

    def status_callback(self, msg):
        self.ui.labelStatus.setText(msg)

    def batch_resize(self):
        in_folder = self.ui.lineInputFolder.text().strip()
        out_folder = self.ui.lineOutputFolder.text().strip()
        # 判断模式和参数
        if self.ui.radioScale.isChecked():
            mode = "scale"
            value = self.ui.spinScale.value()
            desc = f"按比例 {value}%"
        elif self.ui.radioFixedWidth.isChecked():
            mode = "width"
            value = self.ui.spinWidth.value()
            desc = f"固定宽度 {value}"
        else:
            mode = "height"
            value = self.ui.spinHeight.value()
            desc = f"固定高度 {value}"
        resizer = BatchResizer(in_folder=in_folder, out_folder=out_folder, mode=mode, value=value, status_callback=self.status_callback)
        # 校验文件夹
        valid, msg = resizer.validate_folders()
        if not valid:
            self.ui.labelStatus.setText(msg)
            return
        # 加载图片路径
        self.image_paths = resizer.load_image_paths()
        if not self.image_paths:
            self.ui.labelStatus.setText("输入文件夹中没有图片文件")
            return
        total = len(self.image_paths)
        self.ui.labelStatus.setText(f"开始批量缩放 ({desc}) 共 {total} 张图片...")
        resizer.process_images()
        self.ui.labelStatus.setText(f"完成: 共 {total} 张图片处理完毕，保存至 {out_folder}")
        # 弹出 消息框
        QMessageBox.information(self, "批量缩放完成", f"已处理 {total} 张图片，保存至 {out_folder}")
        # 然后打开输出文件夹
        if os.path.exists(out_folder):
            os.startfile(out_folder)


    def save_default_paths(self):
        in_folder = self.ui.lineInputFolder.text().strip()
        out_folder = self.ui.lineOutputFolder.text().strip()
        if in_folder and out_folder:
            data = {"input": in_folder, "output": out_folder}
            with open("default_paths.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.ui.labelStatus.setText("默认路径已保存")
        else:
            self.ui.labelStatus.setText("请先选择输入和输出文件夹")

    def load_default_paths(self):
        import os
        path = "default_paths.json"
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.ui.lineInputFolder.setText(data.get("input", ""))
                self.ui.lineOutputFolder.setText(data.get("output", ""))
            except Exception:
                pass

    def clear_list(self):
        self.image_paths = []
        self.ui.listImages.clear()
        self.ui.labelStatus.setText("已清空图片列表")
        self.update_mode()

    def remove_images(self):
        selected_items = self.ui.listImages.selectedItems()
        if not selected_items:
            self.ui.labelStatus.setText("请先选择要删除的图片")
            return
        for item in selected_items:
            self.ui.listImages.takeItem(self.ui.listImages.row(item))
            self.image_paths.remove(item.text())
        self.ui.labelStatus.setText(f"已删除 {len(selected_items)} 张图片")
        if not self.image_paths:
            self.update_mode()
