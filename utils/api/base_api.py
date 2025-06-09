import requests

class BaseAPI:
    def send_api(self,req):
        return requests.request(**req).json()
