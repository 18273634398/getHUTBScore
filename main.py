from utils.api.logIn import LogIn
from utils.api.getPhoneCode import GetPhoneCode
from utils.log_util import logger
from utils.function import Function
from utils.api.getAccount import GetAccount
from utils.api.getUID import GetUID

mode = int(input("请输入登录模式：1-手机验证码登录，2-密码登录，3-cookie登录，4-获取账号信息\t请输入："))
f = Function()
if mode == 1:
    username = input("请输入手机：")
    res = GetPhoneCode().get_phone_code(username)
    if res:
        psw_or_code = input("请输入验证码：")
        session = LogIn().login(username, psw_or_code, mode)
        f.get_functions()
        function_id = input("请输入功能编号：")
        f.function(function_id, session)

    else:
        logger.info(res)
elif mode == 2:
    print("暂不支持密码登录")
elif mode == 3:
    session = LogIn().login(None, None, 3)
    f.get_functions()
    function_id = input("请输入功能编号：")
    Function().function(function_id, session)
elif mode == 4:
    true_name = input("请输入真实姓名：")
    id_card = input("请输入身份证号：")
    GetAccount().get_account(true_name, id_card,GetUID().get_uid())
