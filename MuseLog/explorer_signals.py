
from PySide6.QtCore import QObject, Signal

class ExplorerSignalManager(QObject):
    # 定义删除选中的动画序列帧信号
    delete_selected_animation_sequence = Signal()
# 创建全局的 signal_manager 实例
signal_manager = ExplorerSignalManager()