from ads_power.modules.browser import Browser
from ads_power.modules.extensions import Extensions
from ads_power.modules.groups import Groups
from ads_power.modules.profiles import Profiles


class Client:
    def __init__(self, api_key: str, api_uri: str) -> None:
        self._api_key = api_key
        self.api_uri = api_uri

        self.browser = Browser(api_key=self._api_key, api_uri=self.api_uri)
        self.extensions = Extensions(api_key=self._api_key, api_uri=self.api_uri)
        self.groups = Groups(api_key=self._api_key, api_uri=self.api_uri)
        self.profiles = Profiles(api_key=self._api_key, api_uri=self.api_uri)
