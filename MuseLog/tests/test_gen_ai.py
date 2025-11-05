import os
import time  
# 通过 pip install 'volcengine-python-sdk[ark]' 安装方舟SDK
from volcenginesdkarkruntime import Ark
from dotenv import load_dotenv
import json

load_dotenv()


# 请确保在项目根目录的 .env 文件中设置 ARK_API_KEY=xxxxx
ark_api_key = os.environ.get("ARK_API_KEY")

if not ark_api_key:
    raise RuntimeError("缺少 ARK_API_KEY，请在 .env 或环境变量中配置。")


# 初始化Ark客户端
client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=ark_api_key,
)

if __name__ == "__main__":
    print("----- create request -----")
    
    # 读取 prompt_params.json 中的 image_url 参数
    with open("prompt_params.json", "r", encoding="utf-8") as f:
        prompt_params = json.load(f)
        image_url = prompt_params.get("image_url", {}).get("url")
    if not image_url:
        raise RuntimeError("prompt_params.json 中缺少 image_url 参数。")
    
    create_result = client.content_generation.tasks.create(
        model="doubao-seedance-1-0-pro-250528", # 模型 Model ID 已为您填入
        content=[
            {
                # 文本提示词与参数组合
                "type": "text",
                "text": "无人机以极快速度穿越复杂障碍或自然奇观，带来沉浸式飞行体验  --resolution 480p  --duration 3 --camerafixed true --watermark false"
            },
            { # 若仅需使用文本生成视频功能，可对该大括号内的内容进行注释处理，并删除上一行中大括号后的逗号。
                # 首帧图片URL
                "type": "image_url",
                "image_url": image_url
            }
        ]
    )
    print(create_result)

    # 轮询查询部分
    print("----- polling task status -----")
    task_id = create_result.id
    while True:
        get_result = client.content_generation.tasks.get(task_id=task_id)
        status = get_result.status
        if status == "succeeded":
            print("----- task succeeded -----")
            print(get_result)
            break
        elif status == "failed":
            print("----- task failed -----")
            print(f"Error: {get_result.error}")
            break
        else:
            print(f"Current status: {status}, Retrying after 3 seconds...")
            time.sleep(3)

# 更多操作请参考下述网址
# 查询视频生成任务列表：https://www.volcengine.com/docs/82379/1521675
# 取消或删除视频生成任务：https://www.volcengine.com/docs/82379/1521720