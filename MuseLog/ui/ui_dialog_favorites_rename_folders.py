# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog_favorites_rename_folders.ui'
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

class Ui_DialogFavoritesRenameFolder(object):
    def setupUi(self, DialogFavoritesRenameFolder):
        if not DialogFavoritesRenameFolder.objectName():
            DialogFavoritesRenameFolder.setObjectName(u"DialogFavoritesRenameFolder")
        DialogFavoritesRenameFolder.resize(383, 155)
        self.verticalLayout = QVBoxLayout(DialogFavoritesRenameFolder)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widget_2 = QWidget(DialogFavoritesRenameFolder)
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

        self.widget = QWidget(DialogFavoritesRenameFolder)
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

        self.buttonBox = QDialogButtonBox(DialogFavoritesRenameFolder)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(DialogFavoritesRenameFolder)
        self.buttonBox.accepted.connect(DialogFavoritesRenameFolder.accept)
        self.buttonBox.rejected.connect(DialogFavoritesRenameFolder.reject)

        QMetaObject.connectSlotsByName(DialogFavoritesRenameFolder)
    # setupUi

    def retranslateUi(self, DialogFavoritesRenameFolder):
        DialogFavoritesRenameFolder.setWindowTitle(QCoreApplication.translate("DialogFavoritesRenameFolder", u"\u91cd\u547d\u540d\u6587\u4ef6\u5939", None))
        self.label.setText(QCoreApplication.translate("DialogFavoritesRenameFolder", u"\u540d\u79f0", None))
        self.labelParentPath.setText(QCoreApplication.translate("DialogFavoritesRenameFolder", u"\u7236\u8282\u70b9\u8def\u5f84\uff1a \u6536\u85cf\u5939/AA/BB", None))
    # retranslateUi

