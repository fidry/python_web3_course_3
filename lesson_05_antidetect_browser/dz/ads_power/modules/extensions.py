from ads_power.modules.base import Base


class Extensions(Base):
    def category_list(
            self,
            page: str = '1',
            page_size: str = '1',
    ):
        path = '/api/v1/application/list'
        method = 'GET'
        params = {
            'page': page,
            'page_size': page_size,
        }

        return self.make_request(
            method=method,
            request_path=self.api_uri + path,
            params=params
        )


# ---------------------------------------------------------------------------------------
# import config
#
# extensions = Extensions(api_key=config.ADS_API_KEY, api_uri=config.ADS_API_URI)
# print(extensions.category_list())
# ---------------------------------------------------------------------------------------
