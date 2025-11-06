
import logging
from pathlib import Path
from PIL import Image
import os
import time

from MuseLog.GTools.gradio_service import GradioService
from MuseLog.explorer_signals import signal_manager

class ImageProcessor:
    """
    处理图像的工具类, 单例模式，
    功能：
    - 去除图片背景
    """
    
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ImageProcessor, cls).__new__(cls)
        return cls._instance

    # 初始化并绑定信号槽
    def InitServices(self) -> None:        
        signal_manager.remove_background_from_sequence_frames.connect(self.on_remove_background_from_sequence_frames)
        signal_manager.resize_sequence_frames.connect(self.on_resize_sequence_frames)
        #
        try:
            self.resample_filter = Image.Resampling.LANCZOS  # type: ignore[attr-defined]
        except AttributeError:
            self.resample_filter = Image.LANCZOS

    def on_remove_background_from_sequence_frames(self, tab_id: str, image_dir_path: str) -> None:
        """
        处理去除序列帧图片背景的信号
        """
        logging.info("收到去除序列帧图片背景请求, tab_id: %s, path: %s", tab_id, image_dir_path)
        # 计时一下
        start_time = time.monotonic()
        success = self.remove_background_batch(image_dir_path)
        end_time = time.monotonic()
        elapsed = end_time - start_time
        if success:
            message = f"去除序列帧图片背景请求已完成: {image_dir_path}, 耗时: {elapsed:.2f} 秒"
            logging.info(message)
            # 发送信号通知界面更新
            signal_manager.gui_notify_msg_to_app.emit(message)
        else:
            message = f"去除序列帧图片背景请求失败: {image_dir_path}, 耗时: {elapsed:.2f} 秒"
            logging.warning(message)
            signal_manager.gui_notify_msg_to_app.emit(message)

    def remove_background_batch(self, image_dir_path: str) -> bool:
        """
        批量去除图片背景
        """
        target_dir = Path(image_dir_path).parent / "透明底_images"
        target_dir.mkdir(exist_ok=True)
        image_paths = []
        for image_file in Path(image_dir_path).glob("*.png"):
            image_paths.append(str(image_file))

        results = GradioService.get_instance().remove_background_batch(image_paths, str(target_dir))
        if not results:
            logging.error("批量去除图片背景失败")
            return False
        else:
            logging.info("已发送批量去除图片背景请求, 数量: %d", len(results))
            return True

        
    def remove_background(self, image_dir_path: str) -> bool:
        """
        去除图片背景
        """
        # 扫描目录下的所有的png图片
        folder_path = Path(image_dir_path)
        if not folder_path.is_dir():
            logging.warning("提供的路径不是目录: %s", image_dir_path)
            return False
        png_files = list(folder_path.glob("*.png"))
        if not png_files:
            logging.info("目录下没有找到png图片: %s", image_dir_path)
            return False
        # 在 image_dir_path 同级目录创建一个 透明底_frames 目录
        transparent_frames_dir = folder_path.parent / "透明底_frames"
        transparent_frames_dir.mkdir(exist_ok=True)
        target_image_dir = transparent_frames_dir
        
        # 发送给 gradio 服务处理
        for image_path in png_files:
            target_image_path = target_image_dir / image_path.name
            GradioService.get_instance().remove_image_background(image_path, str(target_image_path))
        logging.info("已发送 %d 张图片去除背景请求: %s", len(png_files), image_dir_path)
        return True

    def on_resize_sequence_frames(self, tab_id: str, image_dir_path: str) -> None:
        """
        处理缩放序列帧图片的信号
        """
        logging.info("收到缩放序列帧图片请求, tab_id: %s, path: %s", tab_id, image_dir_path)
        
        # 在同级目录创建一个 preds-BiRefNet_resize 目录
        resized_frames_dir = Path(image_dir_path).parent / "preds-BiRefNet_resize"
        
        success = self.resize_sequence_frames(image_dir_path, str(resized_frames_dir))
        if success:
            logging.info("已发送缩放序列帧图片请求, tab_id: %s, path: %s", tab_id, image_dir_path)
            # 发送信号通知界面更新
            signal_manager.gui_notify_msg_to_app.emit(f"缩放序列帧图片请求已完成: {image_dir_path}")
        else:
            logging.warning("缩放序列帧图片请求失败, tab_id: %s, path: %s", tab_id, image_dir_path)
            signal_manager.gui_notify_msg_to_app.emit(f"缩放序列帧图片请求失败: {image_dir_path}")

    def resize_sequence_frames(self, image_dir_path: str, target_dir_path: str) -> bool:
        """
        缩放序列帧图片到 512x512
        """
        folder_path = Path(image_dir_path)
        if not folder_path.is_dir():
            logging.warning("提供的路径不是目录: %s", image_dir_path)
            return False
        png_files = list(folder_path.glob("*.png"))
        if not png_files:
            logging.info("目录下没有找到png图片: %s", image_dir_path)
            return False
        
        target_folder = Path(target_dir_path)
        target_folder.mkdir(parents=True, exist_ok=True)

        for image_path in png_files:
            try:
                with Image.open(image_path) as img:                    
                    img = img.resize((512, 512), self.resample_filter)
                    target_image_path = target_folder / image_path.name
                    img.save(target_image_path)
            except Exception as e:
                logging.error("处理图片失败: %s, 错误: %s", image_path, str(e))
                continue
        logging.info("已发送 %d 张图片缩放请求: %s", len(png_files), image_dir_path)
        return True