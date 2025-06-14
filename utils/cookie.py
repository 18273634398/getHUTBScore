from utils.log_util import logger
import requests
import json

class Cookie:
    def get_cookie(self):
        try:
            # 从本地文件读取cookies
            import os
            # 获取当前文件的绝对路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 构建 cookies.json 的绝对路径
            cookies_path = os.path.join(current_dir, '..', 'doc', 'cookies.json')
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

    def save_cookie(self, session):
        target_cookies = {}
        for cookie in session.cookies:
            if cookie.name in ['JSESSIONID', 'SERVERID']:
                target_cookies[cookie.name] = cookie.value
        # 保存cookie到文件
        import os
        # 获取当前文件的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建 cookies.json 的绝对路径
        cookies_path = os.path.join(current_dir, '..', 'doc', 'cookies.json')
        with open(cookies_path, 'w', encoding='utf-8') as f:
            json.dump(target_cookies, f, indent=2, ensure_ascii=False)
        logger.info("【保存cookies成功】")

if __name__ == '__main__':
    cookies = Cookie().get_cookie()
    print(cookies)