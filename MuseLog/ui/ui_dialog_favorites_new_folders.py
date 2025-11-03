# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog_favorites_new_folders.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QHBoxLayout, QLabel, QLineEdit, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_DialogFavoritesNewFolder(object):
    def setupUi(self, DialogFavoritesNewFolder):
        if not DialogFavoritesNewFolder.objectName():
            DialogFavoritesNewFolder.setObjectName(u"DialogFavoritesNewFolder")
        DialogFavoritesNewFolder.resize(400, 157)
        self.verticalLayout = QVBoxLayout(DialogFavoritesNewFolder)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(6, 6, 6, 6)
        self.widget_2 = QWidget(DialogFavoritesNewFolder)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setMinimumSize(QSize(0, 40))
        self.widget_2.setMaximumSize(QSize(16777215, 16777215))
        self.horizontalLayout = QHBoxLayout(self.widget_2)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.widget_2)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.lineFolderName = QLineEdit(self.widget_2)
        self.lineFolderName.setObjectName(u"lineFolderName")

        self.horizontalLayout.addWidget(self.lineFolderName)


        self.verticalLayout.addWidget(self.widget_2)

        self.widget = QWidget(DialogFavoritesNewFolder)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, -1)
        self.labelParentPath = QLabel(self.widget)
        self.labelParentPath.setObjectName(u"labelParentPath")

        self.verticalLayout_2.addWidget(self.labelParentPath)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.verticalLayout.addWidget(self.widget)

        self.buttonBox = QDialogButtonBox(DialogFavoritesNewFolder)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(DialogFavoritesNewFolder)
        self.buttonBox.accepted.connect(DialogFavoritesNewFolder.accept)
        self.buttonBox.rejected.connect(DialogFavoritesNewFolder.reject)

        QMetaObject.connectSlotsByName(DialogFavoritesNewFolder)
    # setupUi

    def retranslateUi(self, DialogFavoritesNewFolder):
        DialogFavoritesNewFolder.setWindowTitle(QCoreApplication.translate("DialogFavoritesNewFolder", u"\u65b0\u5efa\u6587\u4ef6\u5939", None))
        self.label.setText(QCoreApplication.translate("DialogFavoritesNewFolder", u"\u540d\u79f0", None))
        self.labelParentPath.setText(QCoreApplication.translate("DialogFavoritesNewFolder", u"\u7236\u8282\u70b9\u8def\u5f84\uff1a \u6536\u85cf\u5939/AA/BB", None))
    # retranslateUi

