# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tab_explorer.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QLineEdit,
    QPushButton, QSizePolicy, QSplitter, QTableWidget,
    QTableWidgetItem, QTreeView, QVBoxLayout, QWidget)

class Ui_TabExplorer(object):
    def setupUi(self, TabExplorer):
        if not TabExplorer.objectName():
            TabExplorer.setObjectName(u"TabExplorer")
        TabExplorer.resize(758, 555)
        self.verticalLayout = QVBoxLayout(TabExplorer)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineAddress = QLineEdit(TabExplorer)
        self.lineAddress.setObjectName(u"lineAddress")

        self.horizontalLayout.addWidget(self.lineAddress)

        self.btnEnter = QPushButton(TabExplorer)
        self.btnEnter.setObjectName(u"btnEnter")

        self.horizontalLayout.addWidget(self.btnEnter)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.splitter = QSplitter(TabExplorer)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.treeView = QTreeView(self.splitter)
        self.treeView.setObjectName(u"treeView")
        self.splitter.addWidget(self.treeView)
        self.rightPanel = QWidget(self.splitter)
        self.rightPanel.setObjectName(u"rightPanel")
        self.rightPanelLayout = QVBoxLayout(self.rightPanel)
        self.rightPanelLayout.setObjectName(u"rightPanelLayout")
        self.rightPanelLayout.setContentsMargins(0, 0, 0, 0)
        self.rightTopPanel = QWidget(self.rightPanel)
        self.rightTopPanel.setObjectName(u"rightTopPanel")
        self.rightTopPanel.setMinimumSize(QSize(0, 40))

        self.rightPanelLayout.addWidget(self.rightTopPanel)

        self.tableMeta = QTableWidget(self.rightPanel)
        if (self.tableMeta.columnCount() < 2):
            self.tableMeta.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableMeta.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableMeta.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.tableMeta.setObjectName(u"tableMeta")

        self.rightPanelLayout.addWidget(self.tableMeta)

        self.splitter.addWidget(self.rightPanel)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(TabExplorer)

        QMetaObject.connectSlotsByName(TabExplorer)
    # setupUi

    def retranslateUi(self, TabExplorer):
        TabExplorer.setWindowTitle(QCoreApplication.translate("TabExplorer", u"\u8d44\u6e90\u6d4f\u89c8", None))
        self.lineAddress.setPlaceholderText(QCoreApplication.translate("TabExplorer", u"\u8bf7\u8f93\u5165\u76ee\u5f55\u8def\u5f84\uff0c\u4f8b\u5982\uff1aD:/data/ai_assets", None))
        self.btnEnter.setText(QCoreApplication.translate("TabExplorer", u"\u8fdb\u5165", None))
        ___qtablewidgetitem = self.tableMeta.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("TabExplorer", u"\u952e", None));
        ___qtablewidgetitem1 = self.tableMeta.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("TabExplorer", u"\u503c", None));
    # retranslateUi

