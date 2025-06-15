import base64
from io import BytesIO
from PIL import Image
import requests

from utils.api.getUID import GetUID
from utils.cookie import Cookie
from utils.log_util import logger
from utils.api.base_api import BaseAPI


class LogIn(BaseAPI):
    """登录类，提供多种登录方式"""
    
    def __init__(self):
        super().__init__()
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        }
    
    def login(self, username, psw_or_code, mode):
        """登录主方法，根据不同模式调用不同的登录方式
        
        Args:
            username: 用户名/手机号
            psw_or_code: 密码或验证码
            mode: 登录模式，1-手机验证码登录，2-账号密码验证码登录，3-Cookie登录
            
        Returns:
            session: 登录成功返回session对象，失败返回None
        """
        if mode == 1:
            return self._login_by_phone_code(username, psw_or_code)
        elif mode == 2:
            return self._login_by_account(username, psw_or_code)
        elif mode == 3:
            return self._login_by_cookie()
        else:
            logger.error(f"不支持的登录模式: {mode}")
            return None
    
    def _login_by_phone_code(self, mobile, code):
        """通过手机验证码登录
        
        Args:
            mobile: 手机号
            code: 验证码
            
        Returns:
            session: 登录成功返回session对象，失败返回None
        """
        # 验证验证码是否正确，正确后服务器将返回账号和临时的密码
        req = {
            "url": f"{self.author_base_url}/lyuapServer/sms/validateCode",
            "method": "POST",
            "json": {
                "code": code,
                "mobile": mobile
            }
        }
        response = self.send_api(req)
        
        if response["meta"]["statusCode"] != 200 or response["meta"]["message"] != "ok":
            logger.info(f"验证码验证失败: {response['meta']['message']}")
            return None
            
        # 获取服务器返回的用户名和密码
        username = response["data"]["userName"]
        password = response["data"]["passWord"]
        
        # 使用获取到的用户名和密码登录
        return self._get_session_with_ticket(username, password, login_type=2)
    
    def _login_by_account(self, username, password):
        """通过账号密码和验证码登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            session: 登录成功返回session对象，失败返回None
        """
        # 获取UID
        uid = GetUID().get_uid()
        
        # 获取验证码
        url = f'{self.author_base_url}/lyuapServer/kaptcha?uid={uid}'
        response = requests.get(url)
        
        # 处理验证码图片
        verify_code_data64 = response.json()['content'].split(",")[1]
        image_data = base64.b64decode(verify_code_data64)
        image_stream = BytesIO(image_data)
        image = Image.open(image_stream)
        image.save("code.png")
        logger.info("【验证码获取成功】验证码已保存至根目录下")
        
        # 获取用户输入的验证码
        captcha_code = input("请输入验证码：")
        
        # 构建登录请求
        payload = {
            'username': username,
            'password': password,
            'service': self.base_url,
            'loginType': None,
            'id': uid,
            'code': captcha_code
        }
        
        # 发送登录请求
        url = f'{self.author_base_url}/lyuapServer/v1/tickets'
        session = requests.Session()
        response = session.post(url, headers=self.headers, data=payload)
        
        # 验证登录结果
        if 'tgt' not in response.text:
            logger.info('登录失败！')
            return None
            
        # 登录成功，获取ticket并访问教务网
        logger.info("【身份验证成功】")
        ticket = response.json()["ticket"]
        target_url = f'{self.base_url}/?ticket={ticket}'
        session.get(target_url)
        logger.info("【进入教务网】")
        
        # 保存cookie
        Cookie().save_cookie(session)
        return session
    
    def _login_by_cookie(self):
        """通过存储的cookie登录
        
        Returns:
            session: 登录成功返回session对象，失败返回None
        """
        try:
            cookies = Cookie().get_cookie()
            if not cookies:
                logger.error("获取Cookie失败")
                return None
                
            session = requests.Session()
            session.cookies.update(cookies)
            if Cookie().vertify_cookie(session):
                logger.info("【使用cookie登录成功】")
                return session
            else:
                logger.info("【使用cookie登录失败】cookie已过期")
                Cookie().clear_cookie()
                return None
        except Exception as e:
            logger.error(f"【使用cookie登录失败】{e}")
            return None
    
    def _get_session_with_ticket(self, username, password, login_type=None):
        """通过用户名和密码获取ticket并创建session
        
        Args:
            username: 用户名
            password: 密码
            login_type: 登录类型，默认为None
            
        Returns:
            session: 登录成功返回session对象，失败返回None
        """
        # 构建登录请求
        payload = {
            'username': username,
            'password': password,
            'service': f'{self.base_url}/',
            'loginType': login_type
        }
        url = f'{self.author_base_url}/lyuapServer/v1/tickets'
        
        # 发送登录请求
        session = requests.Session()
        response = session.post(url, headers=self.headers, data=payload)
        
        # 验证登录结果
        if 'tgt' not in response.text:
            logger.info('登录失败！')
            return None
            
        # 登录成功，获取ticket并访问教务网
        logger.info("【身份验证成功】")
        ticket = response.json()["ticket"]
        target_url = f'{self.base_url}/?ticket={ticket}'
        session.get(target_url, allow_redirects=True)
        
        # 保存cookie
        Cookie().save_cookie(session)
        return session