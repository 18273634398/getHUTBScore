from utils.api.base_api import BaseAPI


class GetPhoneCode(BaseAPI):
    def __init__(self):
        super().__init__()

    def get_phone_code(self, phone):
        req = {
            "method": "post",
            "url": f"{self.author_base_url}/lyuapServer/login/mobile/generateCode",
            "json":{
                "module": "0",
                "mobile": f"{phone}",
                "username": f"{phone}"
            }
        }
        result = self.send_api(req)
        if not bool(result["data"]):
            return result["meta"]["message"]
        else:
            return True