
import logging
from pathlib import Path
from PIL import Image
import os
import re
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
        signal_manager.optimize_reference_image_filenames.connect(self.on_optimize_reference_image_filenames)
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

    def remove_background(self, image_path: str, target_path: str) -> bool:
        """
        去除单张图片背景
        """
        result = GradioService.get_instance().remove_image_background(image_path, target_path)
        if not result:
            logging.error("去除图片背景失败: %s", image_path)
            return False
        else:
            logging.info("已发送去除图片背景请求: %s", image_path)
            return True

        
    def remove_backgrounds(self, image_dir_path: str) -> bool:
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
    
    def on_optimize_reference_image_filenames(self, tab_id: str, image_dir_path: str) -> None:
        """
        处理优化参考图文件名称的信号
        """
        logging.info("收到优化参考图文件名称请求, tab_id: %s, path: %s", tab_id, image_dir_path)
        success = self.optimize_reference_image_filenames(image_dir_path)
        if success:
            logging.info("已发送优化参考图文件名称请求, tab_id: %s, path: %s", tab_id, image_dir_path)
            # 发送信号通知界面更新
            signal_manager.gui_notify_msg_to_app.emit(f"优化参考图文件名称请求已完成: {image_dir_path}")
            signal_manager.gui_fresh_tab_collect_metadata.emit(tab_id)
        else:
            logging.warning("优化参考图文件名称请求失败, tab_id: %s, path: %s", tab_id, image_dir_path)
            signal_manager.gui_notify_msg_to_app.emit(f"优化参考图文件名称请求失败: {image_dir_path}")
            
    def optimize_reference_image_filenames(self, image_dir_path: str) -> bool:
        # 优化参考图文件名称
        folder_path = Path(image_dir_path)
        # 扫描目录下的所有的图片文件，包括 png 和 jpg， jpeg， bmp， gif, tiff
        if not folder_path.is_dir():
            logging.warning("提供的路径不是目录: %s", image_dir_path)
            return False
        image_files = []
        for ext in ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.jfif", "*.tiff"]:
            image_files.extend(folder_path.glob(ext))
        if not image_files:
            logging.info("目录下没有找到图片文件: %s", image_dir_path)
            return False
        rename_map = {}
        for image_path in image_files:
            # 文件名, 格式如： 8e8fa106-b3e7-41e9-b1bb-53bfbc9bb95d.jfif， 即只有 英文数字和 - 符号， 且长度较长
            filename = image_path.stem
            # whisk 旧：平台格式 f2d5aea3-e001-4ea8-a4c1-040ef2a4d175.jfif， 新： Whisk_1b673c63ffaea4886a145d2442b4ecf1dr.jpeg
            platform_name = "XX平台"
            # 获取扩展名
            ext = image_path.suffix.lower()
            ext_list = [".png", ".jpg", ".jpeg", ".bmp", ".jfif", ".tiff"]
            
            if len(filename) < 10:
                continue
            pattern_new = r"^(?P<platform_name>[^_]+)_([a-z0-9]{34})$"
            match_result_new = re.match(pattern_new, filename)
            
            # 1.0 判断是否是 旧格式
            if ext in ext_list and len(filename) == 36 and all(c.isalnum() or c == '-' for c in filename):
                platform_name = "Whisk平台"
                # 优化文件名为： reference_001.png, reference_002.png, ...
                # 截取最后4位作为文件名
                new_filename = f"{platform_name}_{image_path.stem[-4:]}{ext}"
                target_image_path = folder_path / new_filename
                rename_map[image_path] = target_image_path
            # 判断 是否是 whisk 新格式
            elif ext in ext_list and match_result_new:
                platform_name = "Whisk平台"
                # 优化文件名为： reference_001.png, reference_002.png, ...
                hash_part = match_result_new.groups()[1:]
                if hash_part:
                    new_filename = f"{platform_name}_{hash_part[0][:4]}{ext}"
                    target_image_path = folder_path / new_filename
                    rename_map[image_path] = target_image_path
        if not rename_map:
            logging.info("没有需要优化的参考图文件名称: %s", image_dir_path)
            return True
        # 读取 提示词文件
        prompt_file_path = folder_path / "提示词.json"
        all_lines = []
        if prompt_file_path.exists():
            try:
                with open(prompt_file_path, "r", encoding="utf-8") as f:
                    all_lines = f.readlines()
            except Exception as e:
                logging.error("读取提示词文件失败: %s, 错误: %s", str(prompt_file_path), str(e))
            for i in range(len(all_lines)):
                line = all_lines[i]
                for old_path, new_path in rename_map.items():
                    old_name = old_path.name
                    new_filename = new_path.name
                    if old_name in line:
                        all_lines[i] = line.replace(old_name, new_filename)
                        logging.info("已更新提示词文件中的参考图文件名: %s -> %s", old_name, new_filename)
            # 写回提示词文件
            try:
                with open(prompt_file_path, "w", encoding="utf-8") as f:
                    f.writelines(all_lines)
            except Exception as e:
                logging.error("写入提示词文件失败: %s, 错误: %s", str(prompt_file_path), str(e))
        # 重命名文件
        for old_path, new_path in rename_map.items():
            try:
                old_path.rename(new_path)
                logging.info("已优化文件名: %s -> %s", old_path.name, new_path.name)
            except Exception as e:
                logging.error("重命名文件失败: %s -> %s, 错误: %s", old_path.name, new_path.name, str(e))
                continue
        logging.info("已优化 %d 个参考图文件名称: %s", len(image_files), image_dir_path)
        return True
        