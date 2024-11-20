from dolphin_remote.modules.browser_profiles import BrowserProfiles


class Client:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

        self.browser_profiles = BrowserProfiles(api_key=self._api_key)
