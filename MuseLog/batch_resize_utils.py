import logging
import os
from PIL import Image
from typing import Callable, List, Tuple, Optional


class BatchResizer:
    def __init__(self, in_folder: str, out_folder: str, mode: str, value: int, status_callback: Optional[Callable[[str], None]] = None):
        self.in_folder: str = in_folder
        self.out_folder: str = out_folder
        self.mode: str = mode
        self.value: int = value
        self.status_callback: Optional[Callable[[str], None]] = status_callback
        self.image_paths: List[str] = []

    def validate_folders(self) -> Tuple[bool, str]:
        if not self.in_folder or not os.path.isdir(self.in_folder):
            return False, "请先选择或输入有效的输入文件夹"
        if not self.out_folder:
            return False, "请先选择或输入有效的输出文件夹"
        if not os.path.exists(self.out_folder):
            try:
                os.makedirs(self.out_folder)
            except Exception as e:
                return False, f"无法创建输出文件夹: {str(e)}"
        return True, ""

    def load_image_paths(self) -> List[str]:
        self.image_paths = []
        for fname in os.listdir(self.in_folder):
            if fname.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                path = os.path.join(self.in_folder, fname)
                self.image_paths.append(path)
        return self.image_paths

    def calculate_new_size(self, w: int, h: int) -> Tuple[int, int]:
        if self.mode == "scale":
            scale = self.value / 100.0
            return int(w * scale), int(h * scale)
        elif self.mode == "width":
            new_w = self.value
            new_h = int(h * new_w / w)
            return new_w, new_h
        elif self.mode == "height":
            new_h = self.value
            new_w = int(w * new_h / h)
            return new_w, new_h
        else:
            return w, h

    def process_images(self) -> None:
        if not self.image_paths:
            self.load_image_paths()
        total = len(self.image_paths)
        for idx, path in enumerate(self.image_paths, 1):
            try:
                img = Image.open(path)
                w, h = img.size
                new_w, new_h = self.calculate_new_size(w, h)
                resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                fname = os.path.basename(path)
                out_path = os.path.join(self.out_folder, fname)
                resized.save(out_path)
                logging.info(f"处理图片: {path} -> {out_path}")
                if self.status_callback:
                    self.status_callback(f"处理 {idx}/{total}: {fname}")
            except Exception:
                logging.exception(f"处理图片失败: {path}")
                continue
        if self.status_callback:
            self.status_callback(f"完成: 共 {total} 张图片处理完毕，保存至 {self.out_folder}")
