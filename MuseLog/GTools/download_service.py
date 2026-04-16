import enum
import os
import shutil
import logging
from datetime import datetime
from pathlib import Path

class MediaFileType(enum.Enum):
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    ARCHIVE = "archive"


class DownloadService:
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DownloadService, cls).__new__(cls)
        return cls._instance
    
    def scan_and_move_latest_download(self, target_folder: str, media_type: MediaFileType = MediaFileType.ARCHIVE) -> bool:
        """
        扫描下载目录，找到最新的下载文件夹，并将其内容移动到目标文件夹。
        
        :param target_folder: 目标文件夹路径
        :return: 是否成功完成操作
        """
        download_dir = Path.home() / "Downloads"  # 假设下载目录为用户的 Downloads 目录
        if not download_dir.exists() or not download_dir.is_dir():
            logging.error("下载目录不存在: %s", download_dir)
            return False

        # 获取下载目录下的所有子文件，按修改时间排序，如果最后一个是压缩包，且是今天下载的，则移动到目标文件夹
        all_items = list(download_dir.iterdir())
        if not all_items:
            logging.info("下载目录为空: %s", download_dir)
            return False
        # 按修改时间排序
        all_items.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        latest_item = all_items[0]
        if not latest_item.is_file():
            logging.info("最新下载项不是文件: %s", latest_item)
            return False
        # 检查是否为压缩包文件
        if media_type == MediaFileType.ARCHIVE:
            if latest_item.suffix.lower() not in ['.zip', '.rar', '.7z']:
                logging.info("最新下载项不是压缩包文件: %s", latest_item)
                return False
        elif media_type == MediaFileType.VIDEO:
            if latest_item.suffix.lower() not in ['.mp4', '.mkv', '.avi', '.mov']:
                logging.info("最新下载项不是视频文件: %s", latest_item)
                return False
        # 检查是否为今天下载的文件
        mod_time = datetime.fromtimestamp(latest_item.stat().st_mtime)
        if mod_time.date() != datetime.now().date():
            logging.info("最新下载项不是今天下载的文件: %s", latest_item)
            return False
        # 移动文件到目标文件夹
        target_path = Path(target_folder) / latest_item.name
        shutil.move(latest_item, target_path)
        logging.info("已将最新下载文件拷贝到目标文件夹: %s", target_path)
        return True