import json
import requests


class Base:
    def __init__(self, api_key: str, api_uri: str) -> None:
        self._api_key = api_key
        self.api_uri = api_uri

    def make_request(
            self, method: str, request_path: str, params: dict | None = None
    ) -> dict[str, ...] | None:
        method = method.upper()

        if method == 'POST':
            response = requests.post(url=request_path, json=params).json()
        else:
            response = requests.get(request_path, params=params).json()

        if int(response.get('code')):
            raise Exception(f'API Exception! Code: {response.get("code")}; Message: {response.get("msg")}')

        return response

    def connection_status(self) -> dict:
        path = '/status'
        method = 'GET'

        return self.make_request(
            method=method,
            request_path=self.api_uri + path
        )


# ---------------------------------------------------------------------------------------
# import config
#
# base = Base(api_key=config.ADS_API_KEY, api_uri=config.ADS_API_URI)
# print(base.connection_status())
# ---------------------------------------------------------------------------------------
