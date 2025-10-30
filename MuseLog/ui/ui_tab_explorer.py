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
    QPushButton, QSizePolicy, QSpacerItem, QSplitter,
    QTableWidget, QTableWidgetItem, QTreeView, QVBoxLayout,
    QWidget)

class Ui_TabExplorer(object):
    def setupUi(self, TabExplorer):
        if not TabExplorer.objectName():
            TabExplorer.setObjectName(u"TabExplorer")
        TabExplorer.resize(891, 549)
        self.verticalLayout = QVBoxLayout(TabExplorer)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.topControlWidget = QWidget(TabExplorer)
        self.topControlWidget.setObjectName(u"topControlWidget")
        self.topControlWidget.setMinimumSize(QSize(0, 30))
        self.topControlWidget.setMaximumSize(QSize(16777215, 50))
        self.horizontalLayout2 = QHBoxLayout(self.topControlWidget)
        self.horizontalLayout2.setSpacing(0)
        self.horizontalLayout2.setObjectName(u"horizontalLayout2")
        self.horizontalLayout2.setContentsMargins(0, 0, 0, 0)
        self.btnBack = QPushButton(self.topControlWidget)
        self.btnBack.setObjectName(u"btnBack")
        self.btnBack.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout2.addWidget(self.btnBack)

        self.btnGoUp = QPushButton(self.topControlWidget)
        self.btnGoUp.setObjectName(u"btnGoUp")
        self.btnGoUp.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout2.addWidget(self.btnGoUp)

        self.btnRefresh = QPushButton(self.topControlWidget)
        self.btnRefresh.setObjectName(u"btnRefresh")
        self.btnRefresh.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout2.addWidget(self.btnRefresh)

        self.lineAddress = QLineEdit(self.topControlWidget)
        self.lineAddress.setObjectName(u"lineAddress")

        self.horizontalLayout2.addWidget(self.lineAddress)

        self.btnEnter = QPushButton(self.topControlWidget)
        self.btnEnter.setObjectName(u"btnEnter")

        self.horizontalLayout2.addWidget(self.btnEnter)


        self.verticalLayout.addWidget(self.topControlWidget)

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
        self.rightTopPanel.setMinimumSize(QSize(0, 100))
        self.verticalLayout_2 = QVBoxLayout(self.rightTopPanel)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.buttonWidget = QWidget(self.rightTopPanel)
        self.buttonWidget.setObjectName(u"buttonWidget")
        self.horizontalLayout = QHBoxLayout(self.buttonWidget)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.btnReference = QPushButton(self.buttonWidget)
        self.btnReference.setObjectName(u"btnReference")

        self.horizontalLayout.addWidget(self.btnReference)

        self.btnVideo = QPushButton(self.buttonWidget)
        self.btnVideo.setObjectName(u"btnVideo")

        self.horizontalLayout.addWidget(self.btnVideo)

        self.btnSequenceFrames = QPushButton(self.buttonWidget)
        self.btnSequenceFrames.setObjectName(u"btnSequenceFrames")

        self.horizontalLayout.addWidget(self.btnSequenceFrames)

        self.btnSpine = QPushButton(self.buttonWidget)
        self.btnSpine.setObjectName(u"btnSpine")

        self.horizontalLayout.addWidget(self.btnSpine)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_2.addWidget(self.buttonWidget)

        self.widget_custom_show = QWidget(self.rightTopPanel)
        self.widget_custom_show.setObjectName(u"widget_custom_show")

        self.verticalLayout_2.addWidget(self.widget_custom_show)


        self.rightPanelLayout.addWidget(self.rightTopPanel)

        self.metaDataPanel = QWidget(self.rightPanel)
        self.metaDataPanel.setObjectName(u"metaDataPanel")
        self.metaDataPanel.setMinimumSize(QSize(0, 150))
        self.verticalLayout_3 = QVBoxLayout(self.metaDataPanel)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.otherWidget = QWidget(self.metaDataPanel)
        self.otherWidget.setObjectName(u"otherWidget")
        self.otherWidget.setMinimumSize(QSize(0, 10))
        self.otherWidget.setMaximumSize(QSize(16777215, 16777215))

        self.verticalLayout_3.addWidget(self.otherWidget)

        self.tableMeta = QTableWidget(self.metaDataPanel)
        if (self.tableMeta.columnCount() < 3):
            self.tableMeta.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableMeta.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableMeta.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableMeta.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.tableMeta.setObjectName(u"tableMeta")

        self.verticalLayout_3.addWidget(self.tableMeta)

        self.DetailWidget = QWidget(self.metaDataPanel)
        self.DetailWidget.setObjectName(u"DetailWidget")
        self.DetailWidget.setMinimumSize(QSize(0, 10))

        self.verticalLayout_3.addWidget(self.DetailWidget)


        self.rightPanelLayout.addWidget(self.metaDataPanel)

        self.splitter.addWidget(self.rightPanel)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(TabExplorer)

        QMetaObject.connectSlotsByName(TabExplorer)
    # setupUi

    def retranslateUi(self, TabExplorer):
        TabExplorer.setWindowTitle(QCoreApplication.translate("TabExplorer", u"\u8d44\u6e90\u6d4f\u89c8", None))
        self.topControlWidget.setWindowTitle(QCoreApplication.translate("TabExplorer", u"\u8d44\u6e90\u6d4f\u89c8", None))
        self.btnBack.setText(QCoreApplication.translate("TabExplorer", u"\u8fd4\u56de", None))
        self.btnGoUp.setText(QCoreApplication.translate("TabExplorer", u"\u4e0a\u4e00\u5c42", None))
        self.btnRefresh.setText(QCoreApplication.translate("TabExplorer", u"\u5237\u65b0", None))
        self.lineAddress.setPlaceholderText(QCoreApplication.translate("TabExplorer", u"\u8bf7\u8f93\u5165\u76ee\u5f55\u8def\u5f84\uff0c\u4f8b\u5982\uff1aD:/data/ai_assets", None))
        self.btnEnter.setText(QCoreApplication.translate("TabExplorer", u"\u8fdb\u5165", None))
        self.btnReference.setText(QCoreApplication.translate("TabExplorer", u"\u53c2\u8003\u56fe", None))
        self.btnVideo.setText(QCoreApplication.translate("TabExplorer", u"\u89c6\u9891", None))
        self.btnSequenceFrames.setText(QCoreApplication.translate("TabExplorer", u"\u5e8f\u5217\u5e27", None))
        self.btnSpine.setText(QCoreApplication.translate("TabExplorer", u"spine", None))
        ___qtablewidgetitem = self.tableMeta.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("TabExplorer", u"\u952e", None));
        ___qtablewidgetitem1 = self.tableMeta.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("TabExplorer", u"\u503c", None));
        ___qtablewidgetitem2 = self.tableMeta.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("TabExplorer", u"\u64cd\u4f5c", None));
    # retranslateUi

