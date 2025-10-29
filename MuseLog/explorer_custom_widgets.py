import os
import re
from typing import Any, Dict, Optional, Sequence, Callable

from PySide6.QtWidgets import QWidget, QPushButton, QLineEdit, QComboBox, QSizePolicy

CustomWidgetBuilder = Callable[[QWidget, str, Dict[str, Any]], Sequence[QWidget]]


def resolve_custom_widget_builder(folder: str, meta: Dict[str, Any]) -> Optional[CustomWidgetBuilder]:
    parent_dir_name = os.path.basename(os.path.dirname(os.path.normpath(folder)))
    if parent_dir_name == "序列帧":
        return build_sequence_frames_widgets
    return None


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
    all_animation_types = ["走路", "待机", "死亡", "攻击"]

    combo_animation_type.addItems(all_animation_types)
    if animation_type in all_animation_types:
        pass
    else:
        combo_animation_type.addItem(animation_type)
    combo_animation_type.setCurrentText(animation_type)
    # combo_animation_type 默认太短， 设置最小宽度
    combo_animation_type.setMinimumWidth(100)
    # 最后加一个 spacer
    spacer = QWidget(container)
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    return [
        btn_modify_frame_rate,
        input_frame_rate,
        btn_modify_animation_type,
        combo_animation_type,
        spacer,
    ]
__all__ = [
    "CustomWidgetBuilder",
    "resolve_custom_widget_builder",
    "build_sequence_frames_widgets",
]
