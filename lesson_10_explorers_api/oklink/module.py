class Module:
    key: str
    url: str
    headers: dict[str, ...]
    module: str

    def __init__(self, key: str, url: str, headers: dict[str, ...]) -> None:
        self.key = key
        self.url = url
        self.headers = headers
