import os
import tos
from PIL import Image
from tos import HttpMethodType
from volcenginesdkarkruntime import Ark
from dotenv import load_dotenv


load_dotenv()

# 从环境变量获取 Access Key/API Key信息
ak = os.getenv('VOLC_ACCESSKEY')
sk = os.getenv('VOLC_SECRETKEY')
api_key = os.getenv('ARK_API_KEY')
# 按需替换 Model ID
model_id = 'doubao-seed-1-6-251015'

# 压缩前图片
original_file = "original_image.jpeg"
# 压缩后图片存放路径
compressed_file = "compressed_image.jpeg"
# 压缩的目标图片大小，300KB
target_size = 300 * 1024

# endpoint 和 region 填写Bucket 所在区域对应的Endpoint。
# 以华北2(北京)为例，region 填写 cn-beijing。
# 公网域名endpoint 填写 tos-cn-beijing.volces.com
endpoint, region = "tos-cn-beijing.volces.com", "cn-beijing"
# 对象桶名称
bucket_name = "demo-bucket-test"
# 对象名称，例如 images 下的 compressed_image.jpeg 文件，则填写为 images/compressed_image.jpeg
object_key = "images/compressed_image.jpeg"

def compress_image(input_path, output_path):
    img = Image.open(input_path)
    current_size = os.path.getsize(input_path)

    # 粗略的估计压缩质量，也可从常量开始，逐步减小压缩质量，直到文件大小小于目标大小
    image_quality = int(float(target_size / current_size) * 100)
    img.save(output_path, optimize=True, quality=int(float(target_size / current_size) * 100))

    # 如果压缩后文件大小仍然大于目标大小，则继续压缩
    # 压缩质量递减，直到文件大小小于目标大小
    while os.path.getsize(output_path) > target_size:
        img = Image.open(output_path)
        image_quality -= 10
        if image_quality <= 0:
            break
        img.save(output_path, optimize=True, quality=image_quality)
    return image_quality

def upload_tos(filename, tos_endpoint, tos_region, tos_bucket_name, tos_object_key):
    # 创建 TosClientV2 对象，对桶和对象的操作都通过 TosClientV2 实现
    tos_client, inner_tos_client = tos.TosClientV2(ak, sk, tos_endpoint, tos_region), tos.TosClientV2(ak, sk,
                                                                                                      tos_endpoint,
                                                                                                      tos_region)
    try:
        # 将本地文件上传到目标桶中, filename为本地压缩后图片的完整路径
        tos_client.put_object_from_file(tos_bucket_name, tos_object_key, filename)
        # 获取上传后预签名的 url
        return inner_tos_client.pre_signed_url(HttpMethodType.Http_Method_Get, tos_bucket_name, tos_object_key)
    except Exception as e:
        if isinstance(e, tos.exceptions.TosClientError):
            # 操作失败，捕获客户端异常，一般情况为非法请求参数或网络异常
            print('fail with client error, message:{}, cause: {}'.format(e.message, e.cause))
        elif isinstance(e, tos.exceptions.TosServerError):
            # 操作失败，捕获服务端异常，可从返回信息中获取详细错误信息
            print('fail with server error, code: {}'.format(e.code))
            # request id 可定位具体问题，强烈建议日志中保存
            print('error with request id: {}'.format(e.request_id))
            print('error with message: {}'.format(e.message))
            print('error with http code: {}'.format(e.status_code))
        else:
            print('fail with unknown error: {}'.format(e))
        raise e


if __name__ == "__main__":
    print("----- 压缩图片 -----")
    quality = compress_image(original_file, compressed_file)
    print("Compressed Image Quality: {}".format(quality))

    print("----- 上传至TOS -----")
    pre_signed_url_output = upload_tos(compressed_file, endpoint, region, bucket_name, object_key)
    print("Pre-signed TOS URL: {}".format(pre_signed_url_output.signed_url))

    print("----- 传入图片调用视觉理解模型 -----")
    client = Ark(api_key=api_key)

    # 图片输入:
    completion = client.chat.completions.create(
        # 配置推理接入点
        model=model_id,
        messages=[
            {
                "role": "user",
                "content": [                    
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": pre_signed_url_output.signed_url
                        }
                    },
                    {"type": "text", "text": "Which is the most secure payment app according to Americans?"},
                ],
            }
        ],
    )

    print(completion.choices[0])