import logging
import os
import re
from typing import Any, Dict, Optional, Sequence, Callable

from PySide6.QtWidgets import QWidget, QPushButton, QLineEdit, QComboBox, QSizePolicy, QMessageBox

CustomWidgetBuilder = Callable[[QWidget, str, Dict[str, Any]], Sequence[QWidget]]


def resolve_custom_widget_builder(folder: str, meta: Dict[str, Any]) -> Optional[CustomWidgetBuilder]:
    parent_dir_name = os.path.basename(os.path.dirname(os.path.normpath(folder)))
    folder_name = os.path.basename(os.path.normpath(folder))
    if parent_dir_name == "序列帧":
        return build_sequence_frames_widgets
    if folder_name.lower() == "spine":
        return build_spine_widgets
    if folder_name.lower() == "序列帧":
        return build_sequence_frames_widgets_parent
    return None


ALL_ANIMATION_TYPES = ["走路", "待机", "死亡", "攻击"]


def build_sequence_frames_widgets(container: QWidget, full_folder: str, meta: Dict[str, Any]) -> Sequence[QWidget]:
    folder_name = os.path.basename(os.path.normpath(full_folder))
    frame_rate = 4  # 默认帧率
    animation_type = "待机"  # 默认动画类型
    # folder 格式如： (秒抽8帧)-攻击
    # 分析 folder 中 的 帧率
    pattern_frame_rate = r"(\d+)帧"
    frame_rate_match = re.search(pattern_frame_rate, folder_name)
    if frame_rate_match:
        frame_rate = int(frame_rate_match.group(1))
    # 分析 folder 中 的 动画类型
    pattern_animation_type = r"-(\S+)$"
    animation_type_match = re.search(pattern_animation_type, folder_name)
    if animation_type_match:
        animation_type = animation_type_match.group(1)
    # 尝试从 folder 名称中提取动画类型

    btn_modify_frame_rate = QPushButton("修改帧率", container)
    input_frame_rate = QLineEdit(container)
    input_frame_rate.setMaximumWidth(60)
    input_frame_rate.setText(str(frame_rate))
    btn_modify_animation_type = QPushButton("修改动画类型", container)
    combo_animation_type = QComboBox(container)

    combo_animation_type.addItems(ALL_ANIMATION_TYPES)
    if animation_type in ALL_ANIMATION_TYPES:
        pass
    else:
        combo_animation_type.addItem(animation_type)
    combo_animation_type.setCurrentText(animation_type)
    # combo_animation_type 默认太短， 设置最小宽度
    combo_animation_type.setMinimumWidth(100)
    btn_delete_animation_sequence = QPushButton("删除选中的动画", container)

    def on_delete_animation_sequence_clicked():
        # 弹框确认删除
        reply = QMessageBox.question(container, "确认删除", "您确定要删除选中的动画吗？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 发送删除信号，这里假设有一个全局的信号管理器 signal_manager
            from MuseLog.explorer_signals import signal_manager
            signal_manager.delete_selected_animation_sequence.emit()
    btn_delete_animation_sequence.clicked.connect(on_delete_animation_sequence_clicked)
    # 最后加一个 spacer
    spacer = QWidget(container)
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    return [
        btn_modify_frame_rate,
        input_frame_rate,
        btn_modify_animation_type,
        combo_animation_type,
        btn_delete_animation_sequence,
        spacer,
    ]


def build_spine_widgets(container: QWidget, full_folder: str, meta: Dict[str, Any]) -> Sequence[QWidget]:
    btn_create_spine_export = QPushButton("创建 spine-导出 文件夹", container)

    def on_create_spine_export_clicked():
        parent_dir = os.path.dirname(full_folder)
        spine_export_folder = os.path.join(parent_dir, "spine-导出")
        os.makedirs(spine_export_folder, exist_ok=True)
        QMessageBox.information(container, "创建成功", f"已成功创建 {spine_export_folder}")
    btn_create_spine_export.clicked.connect(on_create_spine_export_clicked)
    spacer = QWidget(container)
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    return [btn_create_spine_export, spacer]


def build_sequence_frames_widgets_parent(container: QWidget, full_folder: str, meta: Dict[str, Any]) -> Sequence[QWidget]:
    btn_create_animation_sequence = QPushButton("创建 动画序列帧", container)

    def on_create_animation_sequence_clicked():
        # (秒抽XX帧)-YY
        frame_rate = 4  # 默认帧率
        animation_type = "空白"  # 默认动画类型
        animation_sequence_folder_name = f"(秒抽{frame_rate}帧)-{animation_type}"
        animation_sequence_folder = os.path.join(full_folder, animation_sequence_folder_name)
        logging.info(f"Creating animation sequence folder at: {animation_sequence_folder}")
        os.makedirs(animation_sequence_folder, exist_ok=True)
        QMessageBox.information(container, "创建成功", f"已成功创建 {animation_sequence_folder}")

    btn_create_animation_sequence.clicked.connect(on_create_animation_sequence_clicked)

    spacer = QWidget(container)
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    return [btn_create_animation_sequence, spacer]


__all__ = [
    "CustomWidgetBuilder",
    "resolve_custom_widget_builder",
    "build_sequence_frames_widgets",
    "build_spine_widgets",

]
