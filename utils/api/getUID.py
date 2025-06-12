from utils.api.base_api import BaseAPI
from utils.log_util import logger

class GetUID(BaseAPI):
    def __init__(self):
        super().__init__()

    def get_uid(self):
        req={
            "url":f"{self.author_base_url}/lyuapServer/kaptcha",
            "method":"GET"
        }
        uid = self.send_api(req)["uid"]
        logger.info(f"【获取UID成功】UID:{uid}")
        return uid
