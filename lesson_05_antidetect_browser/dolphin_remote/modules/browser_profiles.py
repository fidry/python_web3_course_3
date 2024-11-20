from dolphin_remote.modules.base import Base


class BrowserProfiles(Base):
    def list_browser_profiles(
            self,
            limit: str = '50',
            query: str | None = None,
            tags: list[str] | None = None,
            statuses: list[str] | None = None,
            main_websites: list[str] | None = None,
            users: list[str] | None = None,
            page: str = '1'
    ):
        path = 'browser_profiles'
        method = 'GET'

        params = {
            'limit': limit,
            'query': query,
            'tags[]': tags,
            'statuses[]': statuses,
            'mainWebsites[]': main_websites,
            'users[]': users,
            'page': page,
        }

        return self.make_request(
            method=method,
            request_path=f'{self.URI}/{path}',
            params=params
        )

    def create_browser_profile(
            self,
            name: str,
            platform: str = 'windows',
            browser_type: str = 'anty'
    ):
        path = 'browser_profiles'
        method = 'POST'

        # params = {
        #     # todo: попробовать отправить без параметров
        # }

        params = {
            'name': name,
            'platform': platform,
            'browserType': browser_type,
        }

        return self.make_request(
            method=method,
            request_path=f'{self.URI}/{path}',
            params=params
        )

    def update_browser_profile(
            self,
            profile_id: str,
            name: str,
            platform: str = 'windows',
            browser_type: str = 'anty'
    ):
        path = f'browser_profiles/{profile_id}'
        method = 'PATCH'

        # params = {
        #     # todo: попробовать отправить без параметров
        # }

        params = {
            'name': name,
            'platform': platform,
            'browserType': browser_type,
        }

        return self.make_request(
            method=method,
            request_path=f'{self.URI}/{path}',
            params=params
        )

    def delete_browser_profile(
            self,
            profile_id: str,
            force_delete: str = '1',
    ):
        path = f'browser_profiles/{profile_id}'
        method = 'DELETE'

        params = {
            'forceDelete': force_delete,
        }

        return self.make_request(
            method=method,
            request_path=f'{self.URI}/{path}',
            params=params
        )


# ---------------------------------------------------------------------------------------
# import config
#
#
# profiles = BrowserProfiles(api_key=config.DOLPHIN_API_KEY)
# profiles_list = profiles.list_browser_profiles()
# print(profiles_list)
# for profile in profiles_list.get('data'):
#     print(profile)
#
# print(profiles.create_browser_profile(name='lalala'))
#
# print(profiles.update_browser_profile(profile_id='509825128', name='lalala2'))
#
# print(profiles.delete_browser_profile(profile_id='509825128'))
# ---------------------------------------------------------------------------------------
