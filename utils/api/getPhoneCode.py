from utils.api.base_api import BaseAPI


class GetPhoneCode(BaseAPI):
    def get_phone_code(self, phone):
        req = {
            "method": "post",
            "url": "https://cas.hutb.edu.cn/lyuapServer/login/mobile/generateCode",
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


if __name__ == "__main__":
    get_phone_code = GetPhoneCode()
    res = get_phone_code.get_phone_code("18273634398")
    print(res)
