import requests

class BaseAPI:
    def __init__(self):
        self.base_url = "http://jwgl.hutb.edu.cn"
        self.author_base_url = "https://cas.hutb.edu.cn"

    def send_api(self,req):
        return requests.request(**req).json()
