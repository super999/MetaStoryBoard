
from PySide6.QtWidgets import QDialog, QMessageBox, QWidget
from PySide6.QtCore import Qt
from typing import Optional
from pathlib import Path
import os
from MuseLog.ui.ui_dialog_favorites_new_folders import Ui_DialogFavoritesNewFolder
from MuseLog.favorites_store import FavoritesStore
from MuseLog.model.node import FavoriteNode


class DialogFavoritesNewFolder(QDialog):
    """
    Dialog for creating a new folder in favorites.
    Args:
        QDialog (QDialog): The base dialog class.
    """


    def __init__(self, parent: Optional[QWidget] = None, folder_path: str = "", parent_node_id: Optional[int] = None):
        super().__init__(parent)
        self.folder_path = folder_path
        self.parent_node_id = parent_node_id
        self.ui = Ui_DialogFavoritesNewFolder()
        self.ui.setupUi(self)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._favorites_store = FavoritesStore()        
        self.folder_name = os.path.basename(self.folder_path)
        self.ui.lineFolderName.setText(self.folder_name)        
        parent_path = self._favorites_store.get_node_path(parent_node_id) if parent_node_id is not None else "收藏夹根目录"
        self.ui.labelParentPath.setText(parent_path)
    
    def accept(self) -> None:
        folder_name = self.ui.lineFolderName.text().strip()
        if not folder_name:
            QMessageBox.warning(self, "错误", "文件夹名称不能为空！")
            return

        ret = self._favorites_store.add_child_node(
            node_name=folder_name,
            parent_id=self.parent_node_id
        )
        if ret:
            super().accept()
        else:
            QMessageBox.critical(self, "失败", "收藏夹文件夹添加失败！")