from typing import Literal

from fake_useragent import UserAgent

from oklink.utils import async_get, aiohttp_params
from oklink.module import Module


class ChainInfo(Module):
    module: str = 'solana'

    async def info(self):
        action = 'info'

        res = await async_get(
            url=self.url + f'/api/v5/explorer/{self.module}/{action}',
            headers=self.headers
        )

        return res['data']


class BlockData(Module):
    module: str = 'solana'

    async def block_list(self, limit: str = '2', page: str = '1'):
        action = 'block-list'

        params = {
            'limit': limit,
            'page': page,
        }

        res = await async_get(
            url=self.url + f'/api/v5/explorer/{self.module}/{action}',
            params=aiohttp_params(params),
            headers=self.headers
        )

        return res['data']


class TxData(Module):
    module: str = 'solana'

    async def sol_balance_change(self, tx_hash: str, limit: str = '20', page: str = '1'):
        action = 'sol-balance-change'

        params = {
            'txId': tx_hash,
            'limit': limit,
            'page': page,
        }

        res = await async_get(
            url=self.url + f'/api/v5/explorer/{self.module}/{action}',
            params=aiohttp_params(params),
            headers=self.headers
        )

        return res['data']

    async def tx_details(self, tx_hash: str):
        action = 'transaction-fills'

        params = {
            'txId': tx_hash,
        }

        res = await async_get(
            url=self.url + f'/api/v5/explorer/{self.module}/{action}',
            params=aiohttp_params(params),
            headers=self.headers
        )

        return res['data']

    async def tx_list(self, limit: str = '20', page: str = '1'):
        action = 'transaction-list'

        params = {
            'limit': limit,
            'page': page,
        }

        res = await async_get(
            url=self.url + f'/api/v5/explorer/{self.module}/{action}',
            params=aiohttp_params(params),
            headers=self.headers
        )

        return res['data']


class AccountData(Module):
    module: str = 'solana'

    async def balance_list(
            self,
            address: str,
            protocol_type: Literal['token', 'nft'],
            limit: str = '20',
            page: str = '1'
    ):
        action = 'balance-list'

        params = {
            'address': address,
            'protocolType': protocol_type,
            'limit': limit,
            'page': page,
        }

        res = await async_get(
            url=self.url + f'/api/v5/explorer/{self.module}/{action}',
            params=aiohttp_params(params),
            headers=self.headers
        )

        return res['data']

    async def account_type(self, address: str):
        action = 'account-type'

        params = {
            'address': address,
        }

        res = await async_get(
            url=self.url + f'/api/v5/explorer/{self.module}/{action}',
            params=aiohttp_params(params),
            headers=self.headers
        )

        return res['data']

    async def get_sol_balance(self, address: str):
        action = 'account'

        params = {
            'address': address,
        }

        res = await async_get(
            url=self.url + f'/api/v5/explorer/{self.module}/{action}',
            params=aiohttp_params(params),
            headers=self.headers
        )

        return res['data']


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

        self.chain_info = ChainInfo(self.key, self.url, self.headers)
        self.block_data = BlockData(self.key, self.url, self.headers)
        self.tx_data = TxData(self.key, self.url, self.headers)
        self.account_data = AccountData(self.key, self.url, self.headers)
