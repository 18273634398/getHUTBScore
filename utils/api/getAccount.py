from utils.api.base_api import BaseAPI
from utils.log_util import logger


class GetAccount(BaseAPI):

    def get_account(self, true_name, id_card, uid):
        """
        通过姓名和身份证号码查询账户信息
        :param true_name: 姓名
        :param id_card: 身份证号
        :return: 统一身份认证账号
        """
        req = {
            "url": "https://cas.hutb.edu.cn/lyuapServer/checkAccount",
            "method": "get",
            "params": {
                "username": true_name,
                "cardID": id_card,
                "uid": uid
            }
        }
        response = self.send_api(req)
        if response["data"]:
            logger.info(
                f"查询到【{true_name}】的统一身份认证账号为【{response['data'][0]['screenName']}】,当前状态为【{response['data'][0]['status']}】")
            return response["data"][0]["screenName"]
        else:
            logger.error(f"查询{true_name}的统一身份认证账号失败")
            return None
