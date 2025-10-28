# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tab_home.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_TabHome(object):
    def setupUi(self, TabHome):
        if not TabHome.objectName():
            TabHome.setObjectName(u"TabHome")
        TabHome.resize(102, 34)
        self.verticalLayout = QVBoxLayout(TabHome)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(TabHome)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)


        self.retranslateUi(TabHome)

        QMetaObject.connectSlotsByName(TabHome)
    # setupUi

    def retranslateUi(self, TabHome):
        TabHome.setWindowTitle(QCoreApplication.translate("TabHome", u"\u9996\u9875", None))
        self.label.setText(QCoreApplication.translate("TabHome", u"\u8fd9\u91cc\u662f\u9996\u9875\u5185\u5bb9", None))
    # retranslateUi

