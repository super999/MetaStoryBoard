from PySide6.QtWidgets import QMainWindow, QApplication

from MuseLog.explorer import TabExplorerWidget
from MuseLog.tab_favorites_widget import TabFavoritesWidget
from MuseLog.tab_home_widget import TabHomeWidget
from MuseLog.tab_settings_widget import TabSettingsWidget
from MuseLog.tab_video_gen_ai_widget import TabVideoGenAIWidget
from MuseLog.ui.ui_main_window import Ui_MainWindow


class MuseLogMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # 清空设计器默认的tab页，避免tabCloseRequested失效
        self.tabWidget.clear()
        # 连接关闭信号
        self.tabWidget.tabCloseRequested.connect(self.on_tab_close)
        # 连接按钮点击事件
        self.btnHome.clicked.connect(self.open_home_tab)
        self.btnSettings.clicked.connect(self.open_settings_tab)
        # 用于记录已打开的tab页
        self.opened_tabs = {}
        # 默认打开首页和资源浏览tab
        self.open_home_tab()
        self.open_explorer_tab()

        self.btnExplorer = getattr(self, 'btnExplorer', None)
        if self.btnExplorer:
            # 将原“资源浏览”按钮用于打开资源浏览页
            self.btnExplorer.clicked.connect(self.open_explorer_tab)

        self.btnFavorites = getattr(self, 'btnFavorites', None)
        if self.btnFavorites:
            self.btnFavorites.clicked.connect(self.open_favorites_tab)
        self.btnVideoGen.clicked.connect(self.open_video_gen_tab)

    def open_home_tab(self):
        tab_key = 'home'
        if tab_key in self.opened_tabs:
            self.tabWidget.setCurrentIndex(self.opened_tabs[tab_key])
            return
        home_widget = TabHomeWidget()
        index = self.tabWidget.addTab(home_widget, "首页")
        self.opened_tabs[tab_key] = index
        self.tabWidget.setCurrentIndex(index)

    def open_settings_tab(self):
        tab_key = 'settings'
        if tab_key in self.opened_tabs:
            self.tabWidget.setCurrentIndex(self.opened_tabs[tab_key])
            return
        settings_widget = TabSettingsWidget(theme_apply_callback=self.apply_theme)
        index = self.tabWidget.addTab(settings_widget, "设置")
        self.opened_tabs[tab_key] = index
        self.tabWidget.setCurrentIndex(index)

    def open_explorer_tab(self):
        tab_key = 'explorer'
        if tab_key in self.opened_tabs:
            self.tabWidget.setCurrentIndex(self.opened_tabs[tab_key])
            return
        explorer_widget = TabExplorerWidget()
        index = self.tabWidget.addTab(explorer_widget, "资源浏览")
        self.opened_tabs[tab_key] = index
        self.tabWidget.setCurrentIndex(index)

    def open_favorites_tab(self):
        tab_key = 'favorites'
        if tab_key in self.opened_tabs:
            self.tabWidget.setCurrentIndex(self.opened_tabs[tab_key])
            return
        favorites_widget = TabFavoritesWidget()
        index = self.tabWidget.addTab(favorites_widget, "收藏夹")
        self.opened_tabs[tab_key] = index
        self.tabWidget.setCurrentIndex(index)

    def open_video_gen_tab(self):
        tab_key = 'video_gen_ai'
        if tab_key in self.opened_tabs:
            self.tabWidget.setCurrentIndex(self.opened_tabs[tab_key])
            return
        video_gen_widget = TabVideoGenAIWidget()
        index = self.tabWidget.addTab(video_gen_widget, "视频生成AI")
        self.opened_tabs[tab_key] = index
        self.tabWidget.setCurrentIndex(index)

    def on_tab_close(self, index):
        # 移除 opened_tabs 中的记录
        for key, idx in list(self.opened_tabs.items()):
            if idx == index:
                del self.opened_tabs[key]
                break
        self.tabWidget.removeTab(index)

    def apply_theme(self, theme_name):
        from qt_material import apply_stylesheet
        app = QApplication.instance()
        if app:
            apply_stylesheet(app, theme=theme_name)
