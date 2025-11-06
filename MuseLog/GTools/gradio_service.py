import os
from gradio_client import Client, handle_file
import logging
import requests

class GradioService:

    """
    Gradio 服务的配置信息, 单例模式
    通过 GradioService.get_instance() 获取唯一实例
    """
    # _instance = None

    @classmethod
    def get_instance(cls) -> "GradioService":
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.base_url = "http://127.0.0.1:7861"

        """
        from gradio_client import Client, handle_file

        client = Client("http://127.0.0.1:7861/")
        result = client.predict(
                images=handle_file('https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png'),
                resolution="Hello!!",
                weights_file="General",
                api_name="/image"
        )
        print(result)
        """
    # 接口地址 api /image
    # 把图片变为透明底

    def remove_image_background(self, image_path: str, target_image_path: str) -> dict[str] | None:
        try:
            client = Client(self.base_url)
            result = client.predict(
                images=handle_file(image_path),
                resolution="512x512",
                weights_file="General",
                api_name="/image"
            )
            # 例子： result = 'C:\\Users\\xiawe\\AppData\\Local\\Temp\\gradio\\a0a6e63331e8287923a5d81c46239d9b885740af8cd0482336e7c35d4eb7de3c\\image.png'
            if not result or not isinstance(result, str):
                logging.error(f"请求 Gradio 服务去除图片背景失败, 返回结果格式错误: {result}")
                return None
            if not os.path.exists(result):
                logging.error(f"请求 Gradio 服务去除图片背景失败, 返回结果文件不存在: {result}")
                return None
            logging.info(f"成功请求 Gradio 服务去除图片背景: {image_path}, 结果: {result}")
            # 把图片下载到 target_image_path
            os.replace(result, target_image_path)
            return {
                "original_image_path": image_path,
                "processed_image_path": target_image_path
            }
        except Exception as e:
            logging.error("请求 Gradio 服务失败: %s", str(e))
            return None

        """
            from gradio_client import Client, handle_file
            client = Client("http://127.0.0.1:7861/")
            result = client.predict(
                    images=[handle_file('https://github.com/gradio-app/gradio/raw/main/test/test_files/sample_file.pdf')],
                    resolution="Hello!!",
                    weights_file="General",
                    api_name="/batch"
            )
            print(result)
            
            return: Tuple with the following structure:
            [0] list[dict(image: dict(path: str | None (Path to a local file), url: str | None (Publicly available url or base64 encoded image), size: int | None (Size of image in bytes), orig_name: str | None (Original filename), mime_type: str | None (mime type of image), is_stream: bool (Can always be set to False), meta: dict()), caption: str | None) | dict(video: filepath, caption: str | None)]
                The output value that appears in the "抠图结果" Gallery component.

            [1] filepath
                The output value that appears in the "下载蒙版图像." File component.
        """ 

    def remove_background_batch(self, image_paths: list[str], target_dir: str) -> list[dict[str] | None]:
        rm_results = []
        try:
            client = Client(self.base_url)
            handle_files = [handle_file(image_path) for image_path in image_paths]
            result = client.predict(
                images=handle_files,
                resolution="512x512",
                weights_file="General",
                api_name="/batch"
            )
            process_list = result[0]  # type: ignore[index]
            mask_file_path = result[1]  # type: ignore[index]
            # 例子： result = ['C:\\Users\\xiawe\\AppData\\Local\\Temp\\gradio\\...\\image1.png', ...]
            if not result or not isinstance(process_list, list):
                logging.error(f"请求 Gradio 服务批量去除图片背景失败, 返回结果格式错误: {result}")
                return rm_results
            for i, res_dict in enumerate(process_list):
                if not res_dict or not isinstance(res_dict, dict) or "image" not in res_dict:
                    logging.error(f"请求 Gradio 服务批量去除图片背景失败, 返回结果格式错误: {res_dict}")
                    rm_results.append(None)
                    continue
                result_image_path = res_dict["image"]
                if not result_image_path or not isinstance(result_image_path, str):
                    logging.error(f"请求 Gradio 服务批量去除图片背景失败, 返回结果格式错误: {res_dict}")
                    rm_results.append(None)
                    continue
                target_image_path = os.path.join(target_dir, os.path.basename(image_paths[i]))
                os.replace(result_image_path, target_image_path)
                logging.info(f"成功请求 Gradio 服务批量去除图片背景: {image_paths[i]}, 结果: {res_dict}")
                rm_results.append({
                    "original_image_path": image_paths[i],
                    "processed_image_path": target_image_path
                })
            return rm_results
        except Exception as e:
            logging.error("请求 Gradio 服务批量去除图片背景失败: %s", str(e))
            return rm_results
        