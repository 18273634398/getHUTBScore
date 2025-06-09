from utils.api.getScore import GetScore
from utils.api.base_api import BaseAPI
from utils.api.getPhoneCode import GetPhoneCode
import requests

class LogIn(BaseAPI):
    def login(self,username,psw_or_code,mode):
        # 通过手机验证码登录
        if mode == 1:
            req ={
                    "url":"https://cas.hutb.edu.cn/lyuapServer/sms/validateCode",
                    "method":"POST",
                    "json":{
                        "code":f"{psw_or_code}",
                        "mobile":username
                    }
                }
            response = self.send_api(req)
            if response["meta"]["statusCode"] == 200 and response["meta"]["message"] =="ok":
                username = response["data"]["userName"]
                psw_or_code = response["data"]["passWord"]
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
                print("【身份验证成功】")
                # 进入教务网
                extraURL = response.json()["ticket"]
                url = f'http://jwgl.hutb.edu.cn/?ticket={extraURL}'
                response = session.get(url)
                print("【进入教务网】")
                return session
            else:
                print('登录失败！')
                return None



if __name__ == '__main__':
    username = input("请输入手机：")
    mode = 1
    res = GetPhoneCode().get_phone_code(username)
    if res:
        psw_or_code = input("请输入验证码：")
        session = LogIn().login(username,psw_or_code,mode)
        print(GetScore().get_score(session))
    else:
        print(res)




