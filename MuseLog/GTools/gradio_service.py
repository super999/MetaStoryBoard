import os
from gradio_client import Client, handle_file
import logging


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
        import requests
        url = self.base_url + "/image"
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
