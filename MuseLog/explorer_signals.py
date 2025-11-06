
from PySide6.QtCore import QObject, Signal

class ExplorerSignalManager(QObject):
    # 定义删除选中的动画序列帧信号
    delete_selected_animation_sequence = Signal(str)
    # 定义重命名文件夹信号
    rename_folder = Signal(str, str, str)
    # 定义优化视频文件名称信号
    optimize_video_filenames = Signal(str, str)
    # 定义去除序列帧图片背景信号
    remove_background_from_sequence_frames = Signal(str, str)
    # 定义通知 GUI 消息信号
    gui_notify_msg_to_app = Signal(str)
    # 定义缩放序列帧图片信号
    resize_sequence_frames = Signal(str, str)

# 创建全局的 signal_manager 实例

signal_manager = ExplorerSignalManager()
