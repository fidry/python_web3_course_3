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
            cookie: str | None = None,
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

    def update_profile_info(
            self,
            user_id: str,
            proxy: Proxy,
            name: str | None = None,
            domain_name: str | None = None,
            open_urls: list[str] | None = None,
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
            sys_app_cate_id: str = '0',
            fingerprint_config: dict[str, str] | None = None
    ):
        path = '/api/v1/user/update'
        method = 'POST'
        params = {
            'user_id': user_id,
            'user_proxy_config': proxy.get_dict(),
            'name': name,
            'domain_name': domain_name,
            'open_urls': open_urls,
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
            'sys_app_cate_id': sys_app_cate_id,
            'fingerprint_config': fingerprint_config
        }

        return self.make_request(
            method=method,
            request_path=self.api_uri + path,
            params=params
        )

    def query_profile(
            self,
            group_id: str | None = None,
            user_id: str | None = None,
            serial_number: str | None = None,
            user_sort: dict[str, str] | None = None,
            page: str = '1',
            page_size: str = '50'
    ):
        if not user_sort:
            user_sort = {"serial_number": "desc"}

        path = '/api/v1/user/list'
        method = 'GET'
        params = {
            'group_id': group_id,
            'user_id': user_id,
            'serial_number': serial_number,
            'user_sort': user_sort,
            'page': page,
            'page_size': page_size,
        }

        return self.make_request(
            method=method,
            request_path=self.api_uri + path,
            params=params
        )

    def delete_profile(
            self,
            user_ids: list[str]
    ):
        path = '/api/v1/user/delete'
        method = 'POST'
        params = {
            'user_ids': user_ids,
        }

        return self.make_request(
            method=method,
            request_path=self.api_uri + path,
            params=params
        )

    def move_profile(
            self,
            user_ids: list[str],
            group_id: str
    ):
        path = '/api/v1/user/regroup'
        method = 'POST'
        params = {
            'user_ids': user_ids,
            'group_id': group_id,
        }

        return self.make_request(
            method=method,
            request_path=self.api_uri + path,
            params=params
        )

    def delete_cache(self):
        path = '/api/v1/user/delete-cache'
        method = 'POST'
        params = {

        }

        return self.make_request(
            method=method,
            request_path=self.api_uri + path,
            params=params
        )


# ---------------------------------------------------------------------------------------
# import config
# import time
#
#
# # proxy = Proxy()
# proxy = Proxy(proxy_line='http://45.130.130.75:8000@d2PzGQ:KJ7gRq')
# profiles = Profiles(api_key=config.ADS_API_KEY, api_uri=config.ADS_API_URI)
#
# print(profiles.new_profile(group_name='test', proxy=proxy))
# time.sleep(1)
# print(profiles.new_profile(group_name='test', proxy=proxy, name='test_20'))
# time.sleep(1)
# print(profiles.new_profile(group_name='test', proxy=proxy, name='test_3', fingerprint_config=Fingerprint.get_config()))
#
# print(profiles.update_profile_info(user_id='kq2kc44', name='del test', proxy=proxy))
#
# profiles_list = profiles.query_profile()
# for profile in profiles_list.get('data', {}).get('list'):
#     print(profile)
#
# print(profiles.delete_profile(user_ids=['kq2kc44', 'kq2kc3n']))
#
# print(profiles.delete_cache())
# ---------------------------------------------------------------------------------------
