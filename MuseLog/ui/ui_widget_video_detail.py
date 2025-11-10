# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'widget_video_detail.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QTextEdit, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(535, 313)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setSpacing(1)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.widget_2 = QWidget(Form)
        self.widget_2.setObjectName(u"widget_2")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.widget_2)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(16777215, 16))

        self.horizontalLayout_2.addWidget(self.label)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.playButton = QPushButton(self.widget_2)
        self.playButton.setObjectName(u"playButton")

        self.horizontalLayout_2.addWidget(self.playButton)

        self.closeButton = QPushButton(self.widget_2)
        self.closeButton.setObjectName(u"closeButton")

        self.horizontalLayout_2.addWidget(self.closeButton)


        self.verticalLayout.addWidget(self.widget_2)

        self.textEdit = QTextEdit(Form)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setMaximumSize(QSize(16777215, 150))

        self.verticalLayout.addWidget(self.textEdit)

        self.widget_3 = QWidget(Form)
        self.widget_3.setObjectName(u"widget_3")
        self.widget_3.setMaximumSize(QSize(16777215, 30))
        self.horizontalLayout_3 = QHBoxLayout(self.widget_3)
        self.horizontalLayout_3.setSpacing(4)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_3 = QLabel(self.widget_3)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMaximumSize(QSize(80, 16777215))

        self.horizontalLayout_3.addWidget(self.label_3)

        self.comboRefModel = QComboBox(self.widget_3)
        self.comboRefModel.setObjectName(u"comboRefModel")
        self.comboRefModel.setMinimumSize(QSize(0, 30))
        self.comboRefModel.setEditable(True)

        self.horizontalLayout_3.addWidget(self.comboRefModel)

        self.checkQualified = QCheckBox(self.widget_3)
        self.checkQualified.setObjectName(u"checkQualified")
        self.checkQualified.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_3.addWidget(self.checkQualified)


        self.verticalLayout.addWidget(self.widget_3)

        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMaximumSize(QSize(16777215, 16))

        self.verticalLayout.addWidget(self.label_2)

        self.lineEdit = QLineEdit(Form)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setMinimumSize(QSize(0, 30))
        self.lineEdit.setMaximumSize(QSize(16777215, 30))

        self.verticalLayout.addWidget(self.lineEdit)

        self.widget = QWidget(Form)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.btnCopyCfg = QPushButton(self.widget)
        self.btnCopyCfg.setObjectName(u"btnCopyCfg")

        self.horizontalLayout.addWidget(self.btnCopyCfg)

        self.btnPasteCfg = QPushButton(self.widget)
        self.btnPasteCfg.setObjectName(u"btnPasteCfg")

        self.horizontalLayout.addWidget(self.btnPasteCfg)

        self.horizontalSpacer = QSpacerItem(273, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.saveButton = QPushButton(self.widget)
        self.saveButton.setObjectName(u"saveButton")

        self.horizontalLayout.addWidget(self.saveButton)

        self.cancelButton = QPushButton(self.widget)
        self.cancelButton.setObjectName(u"cancelButton")

        self.horizontalLayout.addWidget(self.cancelButton)


        self.verticalLayout.addWidget(self.widget)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label.setText(QCoreApplication.translate("Form", u"\u63d0\u793a\u8bcd", None))
        self.playButton.setText(QCoreApplication.translate("Form", u"\u64ad\u653e", None))
        self.closeButton.setText(QCoreApplication.translate("Form", u"\u5173\u95ed", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"\u53c2\u8003\u6a21\u578b", None))
        self.checkQualified.setText(QCoreApplication.translate("Form", u"\u662f\u5426\u5408\u683c", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\u53c2\u8003\u56fe", None))
        self.btnCopyCfg.setText(QCoreApplication.translate("Form", u"\u590d\u5236\u8bb0\u5f55", None))
        self.btnPasteCfg.setText(QCoreApplication.translate("Form", u"\u7c98\u8d34", None))
        self.saveButton.setText(QCoreApplication.translate("Form", u"\u4fdd\u5b58", None))
        self.cancelButton.setText(QCoreApplication.translate("Form", u"\u53d6\u6d88", None))
    # retranslateUi

