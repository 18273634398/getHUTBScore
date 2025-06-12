from utils.api.base_api import BaseAPI
from utils.log_util import logger


class AutoJudge(BaseAPI):
    def __init__(self, session):
        super().__init__() # 调用父类的 __init__ 方法
        self.session = session

    def get_judge_status(self):
        req = {
            "url": f"{self.base_url}/jsxsd/xspj/xspj_find.do", # 使用 self.base_url
            "params": {
                "Ves632DSdyV": "NEW_XSD_JXPJ"
            }
        }
        response = self.session.get(**req)
        if "未查询到数据" in response.text:
            logger.info("未查询到数据，可能是暂未开启评教系统")
            return False
        else:
            logger.info("查询到评教系统处于开启状态")
            return True
