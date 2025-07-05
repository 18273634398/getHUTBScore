# file: api/client.py

import requests
from typing import Dict, Any

class NetworkRequest:
    """网络请求类，封装 requests.Session，用于保持会话状态。"""

    def __init__(self, base_url: str, headers: Dict[str, str] = None, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.requestId = None
        if headers:
            self.session.headers.update(headers)

    def update_headers(self, new_headers: Dict[str, str]):
        """更新会话的请求头。"""
        self.session.headers.update(new_headers)
        print("客户端请求头已更新。")

    def post(self, endpoint: str, json_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """发送POST请求。"""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            response = self.session.post(url, json=json_data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"POST请求失败: {e}")
            raise

