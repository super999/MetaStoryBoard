from qt_material import list_themes
from PySide6.QtWidgets import QWidget

from MuseLog.ui.ui_tab_settings import Ui_TabSettings


class TabSettingsWidget(QWidget):
    def __init__(self, parent=None, theme_apply_callback=None):
        super().__init__(parent)
        self.ui = Ui_TabSettings()
        self.ui.setupUi(self)
        self.theme_apply_callback = theme_apply_callback
        # 填充主题列表
        self.ui.comboTheme.addItems(list_themes())
        # 绑定按钮事件
        self.ui.btnApplyTheme.clicked.connect(self.apply_theme)

    def apply_theme(self):
        theme = self.ui.comboTheme.currentText()
        if self.theme_apply_callback:
            self.theme_apply_callback(theme)

