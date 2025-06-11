import json
from utils.api.getExamSchedule import GetExamSchedule
from utils.api.getClassSchedule import GetClassSchedule
from utils.api.getCookie import GetCookie
from utils.log_util import logger
from utils.api.getScore import GetScore
from utils.api.base_api import BaseAPI
from utils.api.getPhoneCode import GetPhoneCode
import requests

class LogIn(BaseAPI):
    def login(self,username,psw_or_code,mode):
        # 通过手机验证码登录
        if mode == 1:
            # 验证验证码是否正确 正确后服务器将返回账号和临时的密码
            req ={
                    "url":"https://cas.hutb.edu.cn/lyuapServer/sms/validateCode",
                    "method":"POST",
                    "json":{
                        "code":f"{psw_or_code}",
                        "mobile":username
                    }
                }
            response = self.send_api(req)

            if response["meta"]["statusCode"] == 200 and response["meta"]["message"] == "ok":
                username = response["data"]["userName"]
                psw_or_code = response["data"]["passWord"]

                # 第一步：获取ticket
                payload = {
                    'username': username,
                    'password': psw_or_code,
                    'service': 'http://jwgl.hutb.edu.cn/',
                    'loginType': 2
                }
                url = 'https://cas.hutb.edu.cn/lyuapServer/v1/tickets'
                headers = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
                }

                session = requests.Session()

                response = session.post(url, headers=headers, data=payload)
                logger.info("【身份验证成功】")

                # 第二步：访问教务网获取cookie
                extraURL = response.json()["ticket"]
                target_url = f'http://jwgl.hutb.edu.cn/?ticket={extraURL}'
                session.get(target_url, allow_redirects=True)
                logger.info("【进入教务网】")

                # 提取指定的cookie
                target_cookies = {}
                for cookie in session.cookies:
                    if cookie.name in ['JSESSIONID', 'SERVERID']:
                        target_cookies[cookie.name] = cookie.value
                logger.info("【保存获取到的Cookie】")
                # 保存cookie到文件
                with open('cookies.json', 'w', encoding='utf-8') as f:
                    json.dump(target_cookies, f, indent=2, ensure_ascii=False)
                return session
            else:
                logger.info('登录失败！')
            return None
        elif mode == 2:
            pass

        # 通过存储的cookie登录
        elif mode == 3:
            cookies = GetCookie().get_cookie()
            session = requests.Session()
            session.cookies.update(cookies)
            logger.info("【使用cookie登录】",cookies)
            return session








if __name__ == '__main__':
    username = input("请输入手机：")
    mode = int(input("请输入登录模式：1-手机验证码登录，2-密码登录，3-cookie登录："))
    if mode == 1:
        res = GetPhoneCode().get_phone_code(username)
        if res:
            psw_or_code = input("请输入验证码：")
            session = LogIn().login(username,psw_or_code,mode)
            GetScore().get_score_level_exam(session)
        else:
            logger.info(res)
    elif mode == 2:
        pass
    elif mode == 3:
        session = LogIn().login(None,None,3)
        # GetScore().get_score_level_exam(session=session)
        # GetClassSchedule().get_class_schedule(session)
        # GetExamSchedule().get_exam_schedule(session)
        GetClassSchedule().get_all_class_schedule(session)
        # GetClassSchedule().get_all_class_schedule(session,'00001','00001','00001')


