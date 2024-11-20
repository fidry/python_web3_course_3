from ads_power.modules.base import Base


class Groups(Base):
    def new_group(self):
        # todo: реализовать
        ...

    def edit_group(self):
        # todo: реализовать
        ...

    def query_group(
            self,
            group_name: str | None = None,
            page: str = '1',
            page_size: str = '1'
    ):
        path = '/api/v1/group/list'
        method = 'GET'
        params = {
            'group_name': group_name,
            'page': page,
            'page_size': page_size,
        }

        return self.make_request(
            method=method,
            request_path=self.api_uri + path,
            params=params
        )

    def get_group_id_by_group_name(self, group_name: str) -> str:
        groups_query = self.query_group(group_name=group_name)
        # {'data': {'list': [{'group_id': '5296878', 'group_name': 'test', 'remark': ''}], 'page': 1, 'page_size': 1}, 'code': 0, 'msg': 'Success'}
        try:
            group_id = groups_query.get('data').get('list')[0].get('group_id')
        except Exception as err:
            raise Exception(f'Can not get group id: {err}')
        return group_id


# ---------------------------------------------------------------------------------------
# import config
# import time
#
# groups = Groups(api_key=config.ADS_API_KEY, api_uri=config.ADS_API_URI)
# print(groups.query_group())
# time.sleep(1)
# print(groups.query_group(group_name='test'))
# ---------------------------------------------------------------------------------------
