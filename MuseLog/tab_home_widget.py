from PySide6.QtWidgets import QWidget

from MuseLog.ui.ui_tab_home import Ui_TabHome


class TabHomeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_TabHome()
        self.ui.setupUi(self)
        # 在这里实现首页tab的逻辑，例如：
        # self.ui.label.setText("欢迎来到首页！")
        # 可以继续添加信号槽、数据处理等1
