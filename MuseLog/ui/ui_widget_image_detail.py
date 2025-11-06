# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'widget_image_detail.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(680, 451)
        Form.setMinimumSize(QSize(0, 451))
        Form.setStyleSheet(u"QFrame #1 {\n"
"    border: 1px solid #222222ff;\n"
"    }\n"
"    ")
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.MainPanel = QWidget(Form)
        self.MainPanel.setObjectName(u"MainPanel")
        self.verticalLayout_2 = QVBoxLayout(self.MainPanel)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.widgetTool = QWidget(self.MainPanel)
        self.widgetTool.setObjectName(u"widgetTool")
        self.widgetTool.setMaximumSize(QSize(16777215, 40))
        self.horizontalLayout_2 = QHBoxLayout(self.widgetTool)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.widgetTool)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.label)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.btnExplorer = QPushButton(self.widgetTool)
        self.btnExplorer.setObjectName(u"btnExplorer")

        self.horizontalLayout_2.addWidget(self.btnExplorer)

        self.btnRemBG = QPushButton(self.widgetTool)
        self.btnRemBG.setObjectName(u"btnRemBG")
        self.btnRemBG.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_2.addWidget(self.btnRemBG)

        self.btnCopyPath = QPushButton(self.widgetTool)
        self.btnCopyPath.setObjectName(u"btnCopyPath")
        self.btnCopyPath.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_2.addWidget(self.btnCopyPath)


        self.verticalLayout_2.addWidget(self.widgetTool)

        self.widget_3 = QWidget(self.MainPanel)
        self.widget_3.setObjectName(u"widget_3")
        self.horizontalLayout = QHBoxLayout(self.widget_3)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.labelImageRect = QLabel(self.widget_3)
        self.labelImageRect.setObjectName(u"labelImageRect")
        self.labelImageRect.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout.addWidget(self.labelImageRect)

        self.widget = QWidget(self.widget_3)
        self.widget.setObjectName(u"widget")
        self.widget.setMaximumSize(QSize(300, 16777215))
        self.verticalLayout_3 = QVBoxLayout(self.widget)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.widget)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_3.addWidget(self.label_2)

        self.textEdit = QTextEdit(self.widget)
        self.textEdit.setObjectName(u"textEdit")

        self.verticalLayout_3.addWidget(self.textEdit)

        self.label_3 = QLabel(self.widget)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout_3.addWidget(self.label_3)

        self.comboRefModel = QComboBox(self.widget)
        self.comboRefModel.setObjectName(u"comboRefModel")

        self.verticalLayout_3.addWidget(self.comboRefModel)

        self.label_4 = QLabel(self.widget)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout_3.addWidget(self.label_4)

        self.comboBox = QComboBox(self.widget)
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setEditable(True)

        self.verticalLayout_3.addWidget(self.comboBox)

        self.widget_2 = QWidget(self.widget)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setMinimumSize(QSize(0, 40))
        self.widget_2.setMaximumSize(QSize(16777215, 50))
        self.horizontalLayout_3 = QHBoxLayout(self.widget_2)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.btnSave = QPushButton(self.widget_2)
        self.btnSave.setObjectName(u"btnSave")

        self.horizontalLayout_3.addWidget(self.btnSave)

        self.btnCancel = QPushButton(self.widget_2)
        self.btnCancel.setObjectName(u"btnCancel")

        self.horizontalLayout_3.addWidget(self.btnCancel)


        self.verticalLayout_3.addWidget(self.widget_2)


        self.horizontalLayout.addWidget(self.widget)


        self.verticalLayout_2.addWidget(self.widget_3)


        self.verticalLayout.addWidget(self.MainPanel)

        self.bottomPanel = QWidget(Form)
        self.bottomPanel.setObjectName(u"bottomPanel")
        self.bottomPanel.setMinimumSize(QSize(0, 40))
        self.bottomPanel.setMaximumSize(QSize(16777215, 50))

        self.verticalLayout.addWidget(self.bottomPanel)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label.setText(QCoreApplication.translate("Form", u"\u9884\u89c8\u56fe", None))
        self.btnExplorer.setText(QCoreApplication.translate("Form", u"\u6253\u5f00\u6587\u4ef6\u5939", None))
        self.btnRemBG.setText(QCoreApplication.translate("Form", u"\u62a0\u56fe-\u900f\u660e\u5e95", None))
        self.btnCopyPath.setText(QCoreApplication.translate("Form", u"\u590d\u5236\u5730\u5740", None))
        self.labelImageRect.setText(QCoreApplication.translate("Form", u"\u56fe\u7247\u663e\u793a\u4f4d\u7f6e", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\u63d0\u793a\u8bcd", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"TextLabel", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"TextLabel", None))
        self.btnSave.setText(QCoreApplication.translate("Form", u"\u4fdd\u5b58", None))
        self.btnCancel.setText(QCoreApplication.translate("Form", u"\u53d6\u6d88", None))
    # retranslateUi

