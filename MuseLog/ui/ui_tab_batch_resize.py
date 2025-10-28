# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tab_batch_resize.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QPushButton, QRadioButton, QSizePolicy, QSpacerItem,
    QSpinBox, QVBoxLayout, QWidget)

class Ui_TabBatchResize(object):
    def setupUi(self, TabBatchResize):
        if not TabBatchResize.objectName():
            TabBatchResize.setObjectName(u"TabBatchResize")
        TabBatchResize.resize(749, 583)
        self.verticalLayout = QVBoxLayout(TabBatchResize)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayoutInput = QHBoxLayout()
        self.horizontalLayoutInput.setObjectName(u"horizontalLayoutInput")
        self.labelInputFolder = QLabel(TabBatchResize)
        self.labelInputFolder.setObjectName(u"labelInputFolder")

        self.horizontalLayoutInput.addWidget(self.labelInputFolder)

        self.lineInputFolder = QLineEdit(TabBatchResize)
        self.lineInputFolder.setObjectName(u"lineInputFolder")

        self.horizontalLayoutInput.addWidget(self.lineInputFolder)

        self.btnSelectInputFolder = QPushButton(TabBatchResize)
        self.btnSelectInputFolder.setObjectName(u"btnSelectInputFolder")

        self.horizontalLayoutInput.addWidget(self.btnSelectInputFolder)


        self.verticalLayout.addLayout(self.horizontalLayoutInput)

        self.horizontalLayoutOutput = QHBoxLayout()
        self.horizontalLayoutOutput.setObjectName(u"horizontalLayoutOutput")
        self.labelOutputFolder = QLabel(TabBatchResize)
        self.labelOutputFolder.setObjectName(u"labelOutputFolder")

        self.horizontalLayoutOutput.addWidget(self.labelOutputFolder)

        self.lineOutputFolder = QLineEdit(TabBatchResize)
        self.lineOutputFolder.setObjectName(u"lineOutputFolder")

        self.horizontalLayoutOutput.addWidget(self.lineOutputFolder)

        self.btnSelectOutputFolder = QPushButton(TabBatchResize)
        self.btnSelectOutputFolder.setObjectName(u"btnSelectOutputFolder")

        self.horizontalLayoutOutput.addWidget(self.btnSelectOutputFolder)


        self.verticalLayout.addLayout(self.horizontalLayoutOutput)

        self.listImages = QListWidget(TabBatchResize)
        self.listImages.setObjectName(u"listImages")
        self.listImages.setMinimumSize(QSize(0, 214))
        self.listImages.setSelectionMode(QAbstractItemView.NoSelection)

        self.verticalLayout.addWidget(self.listImages)

        self.horizontalLayoutListOp = QHBoxLayout()
        self.horizontalLayoutListOp.setObjectName(u"horizontalLayoutListOp")
        self.btnReloadImage = QPushButton(TabBatchResize)
        self.btnReloadImage.setObjectName(u"btnReloadImage")

        self.horizontalLayoutListOp.addWidget(self.btnReloadImage)

        self.btnAddImages = QPushButton(TabBatchResize)
        self.btnAddImages.setObjectName(u"btnAddImages")

        self.horizontalLayoutListOp.addWidget(self.btnAddImages)

        self.btnRemoveImages = QPushButton(TabBatchResize)
        self.btnRemoveImages.setObjectName(u"btnRemoveImages")

        self.horizontalLayoutListOp.addWidget(self.btnRemoveImages)

        self.btnClearList = QPushButton(TabBatchResize)
        self.btnClearList.setObjectName(u"btnClearList")

        self.horizontalLayoutListOp.addWidget(self.btnClearList)

        self.btnSavePath = QPushButton(TabBatchResize)
        self.btnSavePath.setObjectName(u"btnSavePath")

        self.horizontalLayoutListOp.addWidget(self.btnSavePath)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.horizontalLayoutListOp.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayoutListOp)

        self.groupResizeMode = QGroupBox(TabBatchResize)
        self.groupResizeMode.setObjectName(u"groupResizeMode")
        self.verticalLayoutMode = QVBoxLayout(self.groupResizeMode)
        self.verticalLayoutMode.setObjectName(u"verticalLayoutMode")
        self.radioScale = QRadioButton(self.groupResizeMode)
        self.radioScale.setObjectName(u"radioScale")
        self.radioScale.setChecked(True)

        self.verticalLayoutMode.addWidget(self.radioScale)

        self.horizontalLayoutScale = QHBoxLayout()
        self.horizontalLayoutScale.setObjectName(u"horizontalLayoutScale")
        self.labelScale = QLabel(self.groupResizeMode)
        self.labelScale.setObjectName(u"labelScale")

        self.horizontalLayoutScale.addWidget(self.labelScale)

        self.spinScale = QSpinBox(self.groupResizeMode)
        self.spinScale.setObjectName(u"spinScale")
        self.spinScale.setMinimum(1)
        self.spinScale.setMaximum(1000)
        self.spinScale.setValue(100)

        self.horizontalLayoutScale.addWidget(self.spinScale)


        self.verticalLayoutMode.addLayout(self.horizontalLayoutScale)

        self.radioFixedWidth = QRadioButton(self.groupResizeMode)
        self.radioFixedWidth.setObjectName(u"radioFixedWidth")

        self.verticalLayoutMode.addWidget(self.radioFixedWidth)

        self.horizontalLayoutFixedWidth = QHBoxLayout()
        self.horizontalLayoutFixedWidth.setObjectName(u"horizontalLayoutFixedWidth")
        self.labelWidth = QLabel(self.groupResizeMode)
        self.labelWidth.setObjectName(u"labelWidth")

        self.horizontalLayoutFixedWidth.addWidget(self.labelWidth)

        self.spinWidth = QSpinBox(self.groupResizeMode)
        self.spinWidth.setObjectName(u"spinWidth")
        self.spinWidth.setMinimum(1)
        self.spinWidth.setMaximum(10000)
        self.spinWidth.setValue(800)

        self.horizontalLayoutFixedWidth.addWidget(self.spinWidth)


        self.verticalLayoutMode.addLayout(self.horizontalLayoutFixedWidth)

        self.radioFixedHeight = QRadioButton(self.groupResizeMode)
        self.radioFixedHeight.setObjectName(u"radioFixedHeight")

        self.verticalLayoutMode.addWidget(self.radioFixedHeight)

        self.horizontalLayoutFixedHeight = QHBoxLayout()
        self.horizontalLayoutFixedHeight.setObjectName(u"horizontalLayoutFixedHeight")
        self.labelHeight = QLabel(self.groupResizeMode)
        self.labelHeight.setObjectName(u"labelHeight")

        self.horizontalLayoutFixedHeight.addWidget(self.labelHeight)

        self.spinHeight = QSpinBox(self.groupResizeMode)
        self.spinHeight.setObjectName(u"spinHeight")
        self.spinHeight.setMinimum(1)
        self.spinHeight.setMaximum(10000)
        self.spinHeight.setValue(600)

        self.horizontalLayoutFixedHeight.addWidget(self.spinHeight)


        self.verticalLayoutMode.addLayout(self.horizontalLayoutFixedHeight)


        self.verticalLayout.addWidget(self.groupResizeMode)

        self.btnBatchResize = QPushButton(TabBatchResize)
        self.btnBatchResize.setObjectName(u"btnBatchResize")

        self.verticalLayout.addWidget(self.btnBatchResize)

        self.labelStatus = QLabel(TabBatchResize)
        self.labelStatus.setObjectName(u"labelStatus")

        self.verticalLayout.addWidget(self.labelStatus)


        self.retranslateUi(TabBatchResize)

        QMetaObject.connectSlotsByName(TabBatchResize)
    # setupUi

    def retranslateUi(self, TabBatchResize):
        TabBatchResize.setWindowTitle(QCoreApplication.translate("TabBatchResize", u"\u6279\u91cf\u7f29\u653e", None))
        self.labelInputFolder.setText(QCoreApplication.translate("TabBatchResize", u"\u8f93\u5165\u6587\u4ef6\u5939", None))
        self.btnSelectInputFolder.setText(QCoreApplication.translate("TabBatchResize", u"\u6d4f\u89c8...", None))
        self.labelOutputFolder.setText(QCoreApplication.translate("TabBatchResize", u"\u8f93\u51fa\u6587\u4ef6\u5939", None))
        self.btnSelectOutputFolder.setText(QCoreApplication.translate("TabBatchResize", u"\u6d4f\u89c8...", None))
        self.btnReloadImage.setText(QCoreApplication.translate("TabBatchResize", u"\u91cd\u65b0\u52a0\u8f7d", None))
        self.btnAddImages.setText(QCoreApplication.translate("TabBatchResize", u"\u6dfb\u52a0\u56fe\u7247", None))
        self.btnRemoveImages.setText(QCoreApplication.translate("TabBatchResize", u"\u79fb\u9664\u9009\u4e2d\u56fe\u7247", None))
        self.btnClearList.setText(QCoreApplication.translate("TabBatchResize", u"\u6e05\u7a7a\u5217\u8868", None))
        self.btnSavePath.setText(QCoreApplication.translate("TabBatchResize", u"\u4fdd\u5b58\u8def\u5f84", None))
        self.groupResizeMode.setTitle(QCoreApplication.translate("TabBatchResize", u"\u7f29\u653e\u65b9\u5f0f", None))
        self.radioScale.setText(QCoreApplication.translate("TabBatchResize", u"\u6309\u6bd4\u4f8b\u7f29\u653e", None))
        self.labelScale.setText(QCoreApplication.translate("TabBatchResize", u"\u6bd4\u4f8b(%)", None))
        self.radioFixedWidth.setText(QCoreApplication.translate("TabBatchResize", u"\u56fa\u5b9a\u5bbd\u5ea6\u7b49\u6bd4\u7f29\u653e", None))
        self.labelWidth.setText(QCoreApplication.translate("TabBatchResize", u"\u5bbd\u5ea6", None))
        self.radioFixedHeight.setText(QCoreApplication.translate("TabBatchResize", u"\u56fa\u5b9a\u9ad8\u5ea6\u7b49\u6bd4\u7f29\u653e", None))
        self.labelHeight.setText(QCoreApplication.translate("TabBatchResize", u"\u9ad8\u5ea6", None))
        self.btnBatchResize.setText(QCoreApplication.translate("TabBatchResize", u"\u6279\u91cf\u7f29\u653e", None))
        self.labelStatus.setText(QCoreApplication.translate("TabBatchResize", u"\u72b6\u6001\uff1a\u7b49\u5f85\u64cd\u4f5c", None))
    # retranslateUi

