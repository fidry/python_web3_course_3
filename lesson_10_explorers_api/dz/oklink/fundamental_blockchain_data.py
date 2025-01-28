from typing import Literal

from fake_useragent import UserAgent

from oklink.utils import async_get, aiohttp_params
from oklink.module import Module


class FundamentalData(Module):
    module: str = 'blockchain'

    async def summary(self, chain: str | None = None):
        action = 'summary'

        params = {
            'chainShortName': chain,
        }

        res = await async_get(
            url=self.url + f'/api/v5/explorer/{self.module}/{action}',
            params=aiohttp_params(params),
            headers=self.headers
        )

        return res['data']

    async def info(self, chain: str | None = 'eth'):
        action = 'info'

        params = {
            'chainShortName': chain,
        }

        res = await async_get(
            url=self.url + f'/api/v5/explorer/{self.module}/{action}',
            params=aiohttp_params(params),
            headers=self.headers
        )

        return res['data']

    async def fee(self, chain: str | None = 'eth'):
        action = 'fee'

        params = {
            'chainShortName': chain,
        }

        res = await async_get(
            url=self.url + f'/api/v5/explorer/{self.module}/{action}',
            params=aiohttp_params(params),
            headers=self.headers
        )

        return res['data']


class Address(Module):
    module: str = 'address'

    async def address_details(self, address: str, chain: str | None = 'eth'):
        action = 'address-summary'

        params = {
            'chainShortName': chain,
            'address': address,
        }

        res = await async_get(
            url=self.url + f'/api/v5/explorer/{self.module}/{action}',
            params=aiohttp_params(params),
            headers=self.headers
        )

        return res['data']

    async def token_balance(
            self,
            address: str,
            protocol_type: Literal['token_20', 'token_721', 'token_1155'] = 'token_20',
            chain: str | None = 'eth'
    ):
        # https://phemex.com/ru/academy/what-are-erc-721-and-erc-1155
        action = 'token-balance'

        params = {
            'chainShortName': chain,
            'address': address,
            'protocolType': protocol_type,
        }

        res = await async_get(
            url=self.url + f'/api/v5/explorer/{self.module}/{action}',
            params=aiohttp_params(params),
            headers=self.headers
        )

        return res['data']

    async def txlist(
            self,
            address: str,
            page: int = 1,
            limit: int = 50,
            chain: str | None = 'eth'
    ) -> list[dict]:
        action = 'transaction-list'

        params = {
            'chainShortName': chain,
            'address': address,
            'limit': limit,
            'page': page
        }

        res = await async_get(
            url=self.url + f'/api/v5/explorer/{self.module}/{action}',
            params=aiohttp_params(params),
            headers=self.headers
        )

        return res['data'][0]['transactionLists']

    async def txlist_all(
            self,
            address: str,
            chain: str | None = 'eth',
    ) -> list[dict]:
        page = 1
        limit = 50
        txs_lst = []
        txs = await self.txlist(
            address=address,
            page=page,
            limit=limit,
            chain=chain,
        )
        txs_lst += txs
        while len(txs) == limit:
            page += 1
            txs = await self.txlist(
                address=address,
                page=page,
                limit=limit,
                chain=chain,
            )
            txs_lst += txs
        return txs_lst

    async def find_txs(
            self,
            address: str,
            signature: str,
            to: str | None = None,
            chain: str = 'eth',
            txs_lst: list[dict] | None = None
    ):
        if not txs_lst:
            txs_lst = await self.txlist_all(address=address, chain=chain)

        required_transactions = []
        for tx in txs_lst:
            if tx['methodId'] == signature:
                if to and to != tx['to']:
                    continue
                required_transactions.append(tx)

        return required_transactions


class APIFunctions:
    def __init__(self, key: str, url: str) -> None:
        self.key = key
        self.url = url
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'user-agent': UserAgent().chrome,
            'Ok-Access-Key': self.key,
        }

        self.fundamental_data = FundamentalData(self.key, self.url, self.headers)
        self.address = Address(self.key, self.url, self.headers)
