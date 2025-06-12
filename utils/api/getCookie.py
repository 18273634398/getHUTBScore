from utils.log_util import logger
import requests
import json

class GetCookie:
    def get_cookie(self):
        try:
            # 从本地文件读取cookies
            import os
            # 获取当前文件的绝对路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 构建 cookies.json 的绝对路径
            cookies_path = os.path.join(current_dir, '..', '..', 'doc', 'cookies.json')
            with open(cookies_path, 'r') as f:
                cookies = json.load(f)
            # 返回cookies
            return cookies
        except FileNotFoundError:
            logger.info("未找到cookies文件，请先登录获取cookies。")
            return None
        except json.JSONDecodeError:
            logger.info("cookies文件格式错误，请检查文件内容。")
            return None
        except Exception as e:
            logger.info(f"加载cookies时发生错误：{e}")
            return None

if __name__ == '__main__':
    cookies = GetCookie().getCookie()
    print(cookies)