from client import Client
from data.models import Contracts, Settings
from tasks.base import Base
from oklink.fundamental_blockchain_data import APIFunctions


class Controller(Base):
    def __init__(self, client: Client):
        super().__init__(client)

    async def count_swaps(self, txs_lst: list[dict] | None = None):
        # todo: доделать
        settings = Settings()
        chain = 'zksync'

        result_count = 0

        api_oklink = APIFunctions(url='https://www.oklink.com', key=settings.oklink_api_key)

        if not txs_lst:
            txs_lst = await api_oklink.address.txlist_all(
                address=self.client.account.address,
                chain=chain
            )

        # ...
        result_count += len(await api_oklink.address.find_txs(
            address=self.client.account.address,
            signature='...',
            to=Contracts.MAVERICK.address,
            chain=chain,
            txs_lst=txs_lst
        ))

        # ...
        result_count += len(await api_oklink.address.find_txs(
            address=self.client.account.address,
            signature='...',
            to=Contracts.MUTE.address,
            chain=chain,
            txs_lst=txs_lst
        ))

        return result_count

    async def count_mints_nft(self, txs_lst: list[dict] | None = None):
        # todo: доделать
        settings = Settings()
        chain = 'zksync'

        result_count = 0

        api_oklink = APIFunctions(url='https://www.oklink.com', key=settings.oklink_api_key)

        if not txs_lst:
            txs_lst = await api_oklink.address.txlist_all(
                address=self.client.account.address,
                chain=chain
            )

        # ...
        result_count += len(await api_oklink.address.find_txs(
            address=self.client.account.address,
            signature='...',
            to=...,
            chain=chain,
            txs_lst=txs_lst
        ))

        return result_count
