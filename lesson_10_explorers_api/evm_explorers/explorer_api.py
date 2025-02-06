from typing import Literal

from fake_useragent import UserAgent

from evm_explorers.models import Tag, Sort
from evm_explorers import exceptions
from evm_explorers.utils import async_get, aiohttp_params


class Module:
    key: str
    url: str
    headers: dict[str, ...]
    module: str

    def __init__(self, key: str, url: str, headers: dict[str, ...]) -> None:
        self.key = key
        self.url = url
        self.headers = headers


class Account(Module):
    module: str = 'account'

    async def balance(self, address: str, tag: Literal['latest', 'earliest', 'pending'] = Tag.Latest) -> dict[str, ...]:
        action = 'balance'

        if tag not in (Tag.Latest, Tag.Earliest, Tag.Pending):
            raise exceptions.APIException('"tag" parameter have to be either "latest", "earliest" or "pending"')

        params = {
            'module': self.module,
            'action': action,
            'address': address,
            'tag': tag,
            'apikey': self.key,
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def balancemulti(self, addresses: list[str], tag: Literal['latest', 'earliest', 'pending'] = Tag.Latest):
        action = 'balancemulti'

        if tag not in (Tag.Latest, Tag.Earliest, Tag.Pending):
            raise exceptions.APIException('"tag" parameter have to be either "latest", "earliest" or "pending"')

        params = {
            'module': self.module,
            'action': action,
            'address': addresses,
            'tag': tag,
            'apikey': self.key,
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def txlist(
            self, address: str, startblock: int | None = None, endblock: int | None = None,
            page: int | None = None, offset: int | None = None, sort: Literal['asc', 'desc'] = Sort.Asc
    ) -> dict[str, ...]:
        action = 'txlist'

        if sort not in ('asc', 'desc'):
            raise exceptions.APIException('"sort" parameter have to be either "asc" or "desc"')

        params = {
            'module': self.module,
            'action': action,
            'address': address,
            'startblock': startblock,
            'endblock': endblock,
            'page': page,
            'offset': offset,
            'sort': sort,
            'apikey': self.key,
        }

        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)


class Contract(Module):
    module: str = 'contract'

    async def getabi(self, address: str) -> dict[str, ...]:
        action = 'getabi'
        params = {
            'module': self.module,
            'action': action,
            'address': address,
            'apikey': self.key,
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)


class APIFunctions:
    def __init__(self, key: str, url: str) -> None:
        self.key = key
        self.url = url
        self.headers = {'content-type': 'application/json', 'user-agent': UserAgent().chrome}
        self.account = Account(self.key, self.url, self.headers)
        self.contract = Contract(self.key, self.url, self.headers)
        # self.transaction = Transaction(self.key, self.url, self.headers)
        # self.block = Block(self.key, self.url, self.headers)
        # self.logs = Logs(self.key, self.url, self.headers)
        # self.token = Token(self.key, self.url, self.headers)
        # self.gastracker = Gastracker(self.key, self.url, self.headers)
        # self.stats = Stats(self.key, self.url, self.headers)
