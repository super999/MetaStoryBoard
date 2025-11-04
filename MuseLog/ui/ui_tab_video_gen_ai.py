# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tab_video_gen_ai.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QTableWidget, QTableWidgetItem, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_TabVideoGenerateByAI(object):
    def setupUi(self, TabVideoGenerateByAI):
        if not TabVideoGenerateByAI.objectName():
            TabVideoGenerateByAI.setObjectName(u"TabVideoGenerateByAI")
        TabVideoGenerateByAI.resize(900, 674)
        TabVideoGenerateByAI.setAcceptDrops(True)
        self.horizontalLayout_4 = QHBoxLayout(TabVideoGenerateByAI)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.leftPanel = QWidget(TabVideoGenerateByAI)
        self.leftPanel.setObjectName(u"leftPanel")
        self.leftPanel.setMaximumSize(QSize(300, 16777215))
        self.verticalLayout_3 = QVBoxLayout(self.leftPanel)
        self.verticalLayout_3.setSpacing(2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.widget_5 = QWidget(self.leftPanel)
        self.widget_5.setObjectName(u"widget_5")
        self.widget_5.setMinimumSize(QSize(0, 40))

        self.verticalLayout_3.addWidget(self.widget_5)

        self.label_5 = QLabel(self.leftPanel)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(0, 40))

        self.verticalLayout_3.addWidget(self.label_5)

        self.tableResult = QTableWidget(self.leftPanel)
        self.tableResult.setObjectName(u"tableResult")
        self.tableResult.setMaximumSize(QSize(16777215, 16777215))

        self.verticalLayout_3.addWidget(self.tableResult)


        self.horizontalLayout_4.addWidget(self.leftPanel)

        self.rightPanel = QWidget(TabVideoGenerateByAI)
        self.rightPanel.setObjectName(u"rightPanel")
        self.verticalLayout = QVBoxLayout(self.rightPanel)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.widget_301 = QWidget(self.rightPanel)
        self.widget_301.setObjectName(u"widget_301")
        self.widget_301.setMinimumSize(QSize(0, 40))
        self.widget_301.setMaximumSize(QSize(16777215, 50))
        self.horizontalLayout_2 = QHBoxLayout(self.widget_301)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.widget_301)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.lineRefImagePath = QLineEdit(self.widget_301)
        self.lineRefImagePath.setObjectName(u"lineRefImagePath")

        self.horizontalLayout_2.addWidget(self.lineRefImagePath)

        self.btnRefImagePath = QPushButton(self.widget_301)
        self.btnRefImagePath.setObjectName(u"btnRefImagePath")

        self.horizontalLayout_2.addWidget(self.btnRefImagePath)


        self.verticalLayout.addWidget(self.widget_301)

        self.widget_302 = QWidget(self.rightPanel)
        self.widget_302.setObjectName(u"widget_302")
        self.widget_302.setMinimumSize(QSize(0, 100))
        self.widget_302.setMaximumSize(QSize(16777215, 150))
        self.horizontalLayout = QHBoxLayout(self.widget_302)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_4 = QLabel(self.widget_302)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(70, 0))
        self.label_4.setMaximumSize(QSize(70, 16777215))

        self.horizontalLayout.addWidget(self.label_4)

        self.labelRefImagePreview = QLabel(self.widget_302)
        self.labelRefImagePreview.setObjectName(u"labelRefImagePreview")
        self.labelRefImagePreview.setMinimumSize(QSize(100, 100))
        self.labelRefImagePreview.setMaximumSize(QSize(16777215, 16777215))
        self.labelRefImagePreview.setStyleSheet(u" QWidget {\n"
"       border: 1px solid #b81f1fff;\n"
" }")

        self.horizontalLayout.addWidget(self.labelRefImagePreview)


        self.verticalLayout.addWidget(self.widget_302)

        self.widget_303 = QWidget(self.rightPanel)
        self.widget_303.setObjectName(u"widget_303")
        self.widget_303.setMaximumSize(QSize(16777215, 200))
        self.verticalLayout_2 = QVBoxLayout(self.widget_303)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.widget_303)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMaximumSize(QSize(16777215, 30))

        self.verticalLayout_2.addWidget(self.label_2)

        self.textPrompt = QTextEdit(self.widget_303)
        self.textPrompt.setObjectName(u"textPrompt")
        self.textPrompt.setMinimumSize(QSize(0, 180))
        self.textPrompt.setMaximumSize(QSize(16777215, 200))

        self.verticalLayout_2.addWidget(self.textPrompt)


        self.verticalLayout.addWidget(self.widget_303)

        self.widget_3032 = QWidget(self.rightPanel)
        self.widget_3032.setObjectName(u"widget_3032")
        self.widget_3032.setMinimumSize(QSize(0, 50))
        self.widget_3032.setMaximumSize(QSize(16777215, 50))
        self.horizontalLayout_5 = QHBoxLayout(self.widget_3032)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_6 = QLabel(self.widget_3032)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_5.addWidget(self.label_6)

        self.comboModel = QComboBox(self.widget_3032)
        self.comboModel.setObjectName(u"comboModel")

        self.horizontalLayout_5.addWidget(self.comboModel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer)

        self.btnCommit = QPushButton(self.widget_3032)
        self.btnCommit.setObjectName(u"btnCommit")
        self.btnCommit.setMinimumSize(QSize(80, 30))

        self.horizontalLayout_5.addWidget(self.btnCommit)


        self.verticalLayout.addWidget(self.widget_3032)

        self.widget_304 = QWidget(self.rightPanel)
        self.widget_304.setObjectName(u"widget_304")
        self.widget_304.setMinimumSize(QSize(100, 200))
        self.horizontalLayout_3 = QHBoxLayout(self.widget_304)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_3 = QLabel(self.widget_304)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout_3.addWidget(self.label_3)

        self.label_video = QLabel(self.widget_304)
        self.label_video.setObjectName(u"label_video")
        self.label_video.setMinimumSize(QSize(0, 200))
        self.label_video.setStyleSheet(u" QWidget {\n"
"       border: 1px solid #b81f1fff;\n"
" }")

        self.horizontalLayout_3.addWidget(self.label_video)


        self.verticalLayout.addWidget(self.widget_304)


        self.horizontalLayout_4.addWidget(self.rightPanel)


        self.retranslateUi(TabVideoGenerateByAI)

        QMetaObject.connectSlotsByName(TabVideoGenerateByAI)
    # setupUi

    def retranslateUi(self, TabVideoGenerateByAI):
        TabVideoGenerateByAI.setWindowTitle(QCoreApplication.translate("TabVideoGenerateByAI", u"AI\u751f\u6210\u89c6\u9891-\u706b\u5c71\u5f15\u64ce", None))
        self.label_5.setText(QCoreApplication.translate("TabVideoGenerateByAI", u"\u7ed3\u679c\u5217\u8868", None))
        self.label.setText(QCoreApplication.translate("TabVideoGenerateByAI", u"\u53c2\u8003\u56fe\u8def\u5f84", None))
        self.btnRefImagePath.setText(QCoreApplication.translate("TabVideoGenerateByAI", u"\u6d4f\u89c8", None))
        self.label_4.setText(QCoreApplication.translate("TabVideoGenerateByAI", u"\u53c2\u8003\u56fe", None))
        self.labelRefImagePreview.setText(QCoreApplication.translate("TabVideoGenerateByAI", u"TextLabel", None))
        self.label_2.setText(QCoreApplication.translate("TabVideoGenerateByAI", u"\u63d0\u793a\u8bcd", None))
        self.label_6.setText(QCoreApplication.translate("TabVideoGenerateByAI", u"API\u9009\u62e9", None))
        self.btnCommit.setText(QCoreApplication.translate("TabVideoGenerateByAI", u"\u751f\u6210", None))
        self.label_3.setText(QCoreApplication.translate("TabVideoGenerateByAI", u"\u89c6\u9891", None))
        self.label_video.setText(QCoreApplication.translate("TabVideoGenerateByAI", u"TextLabel", None))
    # retranslateUi

