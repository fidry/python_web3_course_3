from ads_power.modules.base import Base
from ads_power.modules.groups import Groups
from ads_power.data.models import Proxy, Fingerprint


class Profiles(Base):
    def new_profile(
            self,
            group_name: str,
            proxy: Proxy,
            name: str | None = None,
            domain_name: str | None = None,
            open_urls: list[str] | None = None,
            repeat_config: list[str] | None = None,
            username: str | None = None,
            password: str | None = None,
            fakey: str | None = None,
            cookie: list[dict[str, str]] | None = None,
            ignore_cookie_error: str = '0',
            ip: str | None = None,
            country: str | None = None,
            region: str | None = None,
            city: str | None = None,
            remark: str | None = None,
            ipchecker: str | None = None,
            sys_app_cate_id: str = '0',
            fingerprint_config: dict[str, str] | None = None
    ):
        path = '/api/v1/user/create'
        method = 'POST'
        params = {
            'group_id': Groups(self._api_key, self.api_uri).get_group_id_by_group_name(group_name),
            'user_proxy_config': proxy.get_dict(),
            'name': name,
            'domain_name': domain_name,
            'open_urls': open_urls,
            'repeat_config': repeat_config,
            'username': username,
            'password': password,
            'fakey': fakey,
            'cookie': cookie,
            'ignore_cookie_error': ignore_cookie_error,
            'ip': ip,
            'country': country,
            'region': region,
            'city': city,
            'remark': remark,
            'ipchecker': ipchecker,
            'sys_app_cate_id': sys_app_cate_id,
            'fingerprint_config': fingerprint_config
        }

        return self.make_request(
            method=method,
            request_path=self.api_uri + path,
            params=params
        )

    def update_profile_info(self):
        # todo: реализовать
        ...

    def query_profile(self):
        # todo: реализовать
        ...

    def delete_profile(self):
        # todo: реализовать
        ...

    def move_profile(self):
        # todo: реализовать
        ...

    def delete_cache(self):
        # todo: реализовать
        ...


# ---------------------------------------------------------------------------------------
# import config
# import time


# proxy = Proxy()
# proxy = Proxy(proxy_line='http://45.130.130.75:8000@d2PzGQ:KJ7gRq')
# profiles = Profiles(api_key=config.ADS_API_KEY, api_uri=config.ADS_API_URI)

# print(profiles.new_profile(group_name='test', proxy=proxy))
# time.sleep(1)
# print(profiles.new_profile(group_name='test', proxy=proxy, name='test_20'))
# time.sleep(1)
# print(profiles.new_profile(group_name='test', proxy=proxy, name='test_3', fingerprint_config=Fingerprint.get_config()))
# ---------------------------------------------------------------------------------------
