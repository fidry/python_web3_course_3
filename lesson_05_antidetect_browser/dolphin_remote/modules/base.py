import json
import requests


class Base:
    URI = 'https://dolphin-anty-api.com'

    def __init__(self, api_key: str) -> None:
        self.__api_key = api_key

    def make_request(
            self, method: str, request_path: str, params: dict | None = None
    ) -> dict[str, ...] | None:
        method = method.upper()

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.__api_key}'
        }

        params = json.dumps(params)
        response = requests.request(method, request_path, headers=headers, data=params).json()

        if not response.get('success', 1):
            raise Exception(f'API Exception! Response: {response}')

        return response
