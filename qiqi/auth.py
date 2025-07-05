# file: api/auth.py

import base64
import os
from client import NetworkRequest  # 从同一个包中导入 client

def _save_captcha_image(image_content: str, save_path: str):
    """私有辅助函数，用于保存验证码图片。"""
    try:
        # 确保目录存在
        directory = os.path.dirname(save_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # 移除base64数据前缀
        if image_content.startswith("data:image/png;base64,"):
            image_content = image_content[len("data:image/png;base64,"):]

        with open(save_path, "wb") as f:
            f.write(base64.b64decode(image_content))
        print(f"验证码图片已保存至: {save_path}")
    except Exception as e:
        print(f"保存验证码图片失败: {e}")

def get_captcha(client: NetworkRequest):
    """
    获取验证码图片。

    Args:
        client: 一个 NetworkRequest 实例，将用于执行所有网络请求。

    Returns:
        bool: 验证码获取是否成功。
    """
    try:
        # 1. 获取 requestId
        print("正在获取 requestId...")
        prepare_response = client.post("/prepare", json_data={})
        request_id = prepare_response.get("requestId")
        if not request_id:
            print("获取 requestId 失败。")
            return False

        print(f"获取到 requestId: {request_id}")
        client.requestId = request_id
        print(f"设置 requestId: {client.requestId}")
        # 2. 获取验证码图片
        print("\n正在获取验证码...")
        captcha_response = client.post("/getLoginCaptcha", json_data={"requestId": request_id})

        save_path = "./captcha.png"
        if captcha_response.get("type") == "image":
            _save_captcha_image(captcha_response["image"]["content"], save_path)

        return True

    except Exception as e:
        print(f"获取验证码失败: {e}")
        return False


def perform_login(client: NetworkRequest, account: str, password: str, captcha: str) -> bool:
    """
    执行完整的登录流程。
    这个函数会修改传入的 client 对象，为其更新 token。

    Args:
        client: 一个 NetworkRequest 实例，将用于执行所有网络请求。
        account: 用户账号。
        password: 用户密码。
        captcha: 用户输入的验证码。

    Returns:
        bool: 登录是否成功。
    """
    try:
        print("\n正在登录...")
        login_data = {
            "account": account,
            "password": password,
            "captcha": captcha,
            "requestId": client.requestId
        }
        client.post("/login", json_data=login_data)

        # 3. 登录成功 若未成功 系统会返回错误信息
        return True


    except Exception as e:
        print(f"登录流程出错，请检查账号或密码是否正确以及验证码是否正确。错误信息: {e}")
        return False