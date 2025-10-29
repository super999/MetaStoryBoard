# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QMainWindow, QPushButton,
    QSizePolicy, QSpacerItem, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1373, 855)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.navWidget = QWidget(self.centralwidget)
        self.navWidget.setObjectName(u"navWidget")
        self.navWidget.setMinimumSize(QSize(120, 0))
        self.navWidget.setMaximumSize(QSize(300, 16777215))
        self.verticalLayout = QVBoxLayout(self.navWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.btnHome = QPushButton(self.navWidget)
        self.btnHome.setObjectName(u"btnHome")

        self.verticalLayout.addWidget(self.btnHome)

        self.btnExplorer = QPushButton(self.navWidget)
        self.btnExplorer.setObjectName(u"btnExplorer")

        self.verticalLayout.addWidget(self.btnExplorer)

        self.btnSettings = QPushButton(self.navWidget)
        self.btnSettings.setObjectName(u"btnSettings")

        self.verticalLayout.addWidget(self.btnSettings)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.horizontalLayout.addWidget(self.navWidget)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setTabsClosable(True)
        self.tab1 = QWidget()
        self.tab1.setObjectName(u"tab1")
        self.tabWidget.addTab(self.tab1, "")
        self.tab2 = QWidget()
        self.tab2.setObjectName(u"tab2")
        self.tabWidget.addTab(self.tab2, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u7075\u7ed8\u56fe\u5377 -\u5143\u6570\u636e\u8bb0\u5f55\u4e0e\u6d4f\u89c8\u5de5\u5177", None))
        self.btnHome.setText(QCoreApplication.translate("MainWindow", u"\u9996\u9875", None))
        self.btnExplorer.setText(QCoreApplication.translate("MainWindow", u"\u8d44\u6e90\u6d4f\u89c8", None))
        self.btnSettings.setText(QCoreApplication.translate("MainWindow", u"\u8bbe\u7f6e", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab1), QCoreApplication.translate("MainWindow", u"Tab 1", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab2), QCoreApplication.translate("MainWindow", u"Tab 2", None))
    # retranslateUi

