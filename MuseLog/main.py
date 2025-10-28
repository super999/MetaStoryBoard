#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2025/10/28 15:21
# @Author  : ChenXiaWen
# @File    : main.py.py
# @Path    : MuseLog/main.py


import logging
import sys
from PySide6.QtWidgets import QApplication

from . import logging_utils
from .main_window import ImageResizeMainWindow
from qt_material import apply_stylesheet, list_themes


def main():
    # 初始化日志
    logging_utils.init_logging()
    logging.info("Image Resize Tool started")
    app = QApplication(sys.argv)
    print(list_themes())
    # 套用“dark_teal.xml”深色主题
    apply_stylesheet(app, theme='dark_cyan.xml')
    window = ImageResizeMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
