
from PySide6.QtWidgets import QDialog, QMessageBox, QWidget
from PySide6.QtCore import Qt
from typing import Optional
from pathlib import Path
import os
from MuseLog.favorites_store import FavoritesStore
from MuseLog.model.node import FavoriteNode
from MuseLog.ui.ui_dialog_favorites_rename_folders import Ui_DialogFavoritesRenameFolder


class DialogFavoritesRenameFolder(QDialog):
    """
    Dialog for renaming a folder in favorites.
    Args:
        QDialog (QDialog): The base dialog class.
    """


    def __init__(self, parent: Optional[QWidget] = None, folder_path: str = "", node: FavoriteNode = None):
        super().__init__(parent)
        self.folder_path = folder_path
        self.node: FavoriteNode = node
        self.ui = Ui_DialogFavoritesRenameFolder()
        self.ui.setupUi(self)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._favorites_store = FavoritesStore()        
        self.folder_name = os.path.basename(self.folder_path)
        self.ui.lineFolderName.setText(self.folder_name)        
        self.ui.labelParentPath.setText("空白")
    
    def accept(self) -> None:
        folder_name = self.ui.lineFolderName.text().strip()
        if not folder_name:
            QMessageBox.warning(self, "错误", "文件夹名称不能为空！")
            return
        ret = self._favorites_store.rename_node(self.node.node_id, folder_name)        
        if ret:
            super().accept()
        else:
            QMessageBox.critical(self, "失败", "收藏夹文件夹重命名失败！")