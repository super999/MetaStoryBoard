# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tab_settings.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QLabel, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_TabSettings(object):
    def setupUi(self, TabSettings):
        if not TabSettings.objectName():
            TabSettings.setObjectName(u"TabSettings")
        TabSettings.resize(307, 183)
        self.verticalLayout = QVBoxLayout(TabSettings)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(TabSettings)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.comboTheme = QComboBox(TabSettings)
        self.comboTheme.setObjectName(u"comboTheme")

        self.verticalLayout.addWidget(self.comboTheme)

        self.btnApplyTheme = QPushButton(TabSettings)
        self.btnApplyTheme.setObjectName(u"btnApplyTheme")

        self.verticalLayout.addWidget(self.btnApplyTheme)


        self.retranslateUi(TabSettings)

        QMetaObject.connectSlotsByName(TabSettings)
    # setupUi

    def retranslateUi(self, TabSettings):
        TabSettings.setWindowTitle(QCoreApplication.translate("TabSettings", u"\u8bbe\u7f6e", None))
        self.label.setText(QCoreApplication.translate("TabSettings", u"\u8fd9\u91cc\u662f\u8bbe\u7f6e\u5185\u5bb9", None))
#if QT_CONFIG(tooltip)
        self.comboTheme.setToolTip(QCoreApplication.translate("TabSettings", u"\u9009\u62e9\u4e3b\u9898\u98ce\u683c", None))
#endif // QT_CONFIG(tooltip)
        self.btnApplyTheme.setText(QCoreApplication.translate("TabSettings", u"\u5e94\u7528\u98ce\u683c", None))
    # retranslateUi

