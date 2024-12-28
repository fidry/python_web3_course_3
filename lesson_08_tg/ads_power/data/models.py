class ProxySoft:
    no_proxy = 'no_proxy'
    other = 'other'


class Proxy:
    proxy_soft: str
    proxy_type: str | None
    proxy_host: str | None
    proxy_port: str | None
    proxy_user: str | None
    proxy_password: str | None

    def __init__(
            self,
            proxy_line: str = '',
            proxy_soft: str = ProxySoft.no_proxy,
            proxy_type: str = 'http'
    ) -> None:
        self.proxy_soft = proxy_soft

        if proxy_line:
            self.proxy_soft = ProxySoft.other
            self.parse_proxy(proxy_line, proxy_type=proxy_type)

    def parse_proxy(self, proxy_line: str, proxy_type: str) -> None:
        """
        examples:
        socks5://ip:port@login:password
        socks5://ip:port:login:password
        """
        if '://' not in proxy_line:
            proxy_line = f'{proxy_type}://{proxy_line}'

        self.proxy_type = proxy_line.split('://')[0]
        pure_proxy = proxy_line.split('://')[1]
        if '@' in proxy_line:
            self.proxy_host, self.proxy_port = pure_proxy.split('@')[0].split(':')
            self.proxy_user, self.proxy_password = pure_proxy.split('@')[1].split(':')
        else:
            self.proxy_host, self.proxy_port, self.proxy_user, self.proxy_password = pure_proxy.split(':')

    def get_line(self) -> str:
        if self.proxy_soft == ProxySoft.no_proxy:
            return ''
        return f'{self.proxy_type}://{self.proxy_user}:{self.proxy_password}@{self.proxy_host}:{self.proxy_port}'

    def get_dict(self) -> dict:
        if self.proxy_soft == ProxySoft.no_proxy:
            return {
                'proxy_soft': ProxySoft.no_proxy
            }

        return {
            'proxy_type': self.proxy_type,
            'proxy_host': self.proxy_host,
            'proxy_port': self.proxy_port,
            'proxy_user': self.proxy_user,
            'proxy_password': self.proxy_password,
            'proxy_soft': self.proxy_soft,
        }


class Fingerprint:
    @staticmethod
    def get_config(
            ua: str | None = None,
            language: str = 'en-US'
    ) -> dict:
        """
        https://localapi-doc-en.adspower.com/docs/Awy6Dg
        """
        fingerprint = {
            "language": [
                language
            ],
            "flash": "block",
            "scan_port_type": "1",
            # "screen_resolution": "1024_600",
            "fonts": [
                "all"
            ],
            "do_not_track": "default",
            "hardware_concurrency": "default",
            "device_memory": "default",
        }

        if ua:
            fingerprint['ua'] = ua

        return fingerprint
