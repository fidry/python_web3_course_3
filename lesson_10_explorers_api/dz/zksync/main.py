import asyncio
from datetime import datetime

from fake_useragent import FakeUserAgent

from zksync.utils import async_get


async def txlist(address: str, page: int = 1, limit: int = 20):
    if limit > 100:
        raise ValueError('limit must not be greater than 100')

    headers = {
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://explorer.zksync.io',
        'priority': 'u=1, i',
        'referer': 'https://explorer.zksync.io/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': FakeUserAgent().chrome,
    }

    params = {
        'address': address,
        'limit': limit,
        'page': page,
        'toDate': str(datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')),
    }

    res = await async_get(
        url='https://block-explorer-api.mainnet.zksync.io/transactions',
        params=params,
        headers=headers
    )

    return res['items']


async def txlist_all(address: str) -> list[dict]:
    page = 1
    limit = 100
    txs_lst = []
    txs = await txlist(
        address=address,
        page=page,
        limit=limit,
    )
    txs_lst += txs
    while len(txs) == limit:
        page += 1
        txs = await txlist(
            address=address,
            page=page,
            limit=limit,
        )
        txs_lst += txs

    return txs_lst
