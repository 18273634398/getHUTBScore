from utils.log_util import logger
import requests
import json

class GetCookie:
    def get_cookie(self):
        try:
            # 从本地文件读取cookies
            with open('cookies.json', 'r') as f:
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