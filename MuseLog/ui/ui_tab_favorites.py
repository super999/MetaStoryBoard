# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tab_favorites.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QListView, QPushButton, QSizePolicy,
    QSpacerItem, QSplitter, QTreeView, QVBoxLayout,
    QWidget)

class Ui_TabFavorites(object):
    def setupUi(self, TabFavorites):
        if not TabFavorites.objectName():
            TabFavorites.setObjectName(u"TabFavorites")
        TabFavorites.resize(1010, 582)
        TabFavorites.setStyleSheet(u" QWidget {\n"
"       border: 1px solid #d3d3d3;\n"
" }")
        self.verticalLayout = QVBoxLayout(TabFavorites)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.topPanel = QWidget(TabFavorites)
        self.topPanel.setObjectName(u"topPanel")
        self.verticalLayout_2 = QVBoxLayout(self.topPanel)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.splitter = QSplitter(self.topPanel)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.leftPanel = QWidget(self.splitter)
        self.leftPanel.setObjectName(u"leftPanel")
        self.leftPanel.setMinimumSize(QSize(200, 100))
        self.leftPanel.setMaximumSize(QSize(300, 16777215))
        self.verticalLayout_4 = QVBoxLayout(self.leftPanel)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.leftPanel)
        self.label.setObjectName(u"label")

        self.verticalLayout_4.addWidget(self.label)

        self.lineFilter = QLineEdit(self.leftPanel)
        self.lineFilter.setObjectName(u"lineFilter")

        self.verticalLayout_4.addWidget(self.lineFilter)

        self.treeView = QTreeView(self.leftPanel)
        self.treeView.setObjectName(u"treeView")

        self.verticalLayout_4.addWidget(self.treeView)

        self.splitter.addWidget(self.leftPanel)
        self.rightPanel = QWidget(self.splitter)
        self.rightPanel.setObjectName(u"rightPanel")
        self.rightPanel.setMinimumSize(QSize(50, 100))
        self.rightPanel.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_3 = QVBoxLayout(self.rightPanel)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.widget = QWidget(self.rightPanel)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_3 = QLabel(self.widget)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.btnAddFolder = QPushButton(self.widget)
        self.btnAddFolder.setObjectName(u"btnAddFolder")

        self.horizontalLayout.addWidget(self.btnAddFolder)


        self.verticalLayout_3.addWidget(self.widget)

        self.listView = QListView(self.rightPanel)
        self.listView.setObjectName(u"listView")

        self.verticalLayout_3.addWidget(self.listView)

        self.splitter.addWidget(self.rightPanel)

        self.verticalLayout_2.addWidget(self.splitter)


        self.verticalLayout.addWidget(self.topPanel)

        self.bottomPanel2 = QWidget(TabFavorites)
        self.bottomPanel2.setObjectName(u"bottomPanel2")
        self.bottomPanel2.setMaximumSize(QSize(16777215, 20))

        self.verticalLayout.addWidget(self.bottomPanel2)


        self.retranslateUi(TabFavorites)

        QMetaObject.connectSlotsByName(TabFavorites)
    # setupUi

    def retranslateUi(self, TabFavorites):
        TabFavorites.setWindowTitle(QCoreApplication.translate("TabFavorites", u"\u6536\u85cf\u5939", None))
        self.label.setText(QCoreApplication.translate("TabFavorites", u"\u6536\u85cf\u5939", None))
        self.label_3.setText(QCoreApplication.translate("TabFavorites", u"\u9879\u76ee", None))
        self.btnAddFolder.setText(QCoreApplication.translate("TabFavorites", u"\u6dfb\u52a0\u6587\u4ef6\u5939", None))
    # retranslateUi

