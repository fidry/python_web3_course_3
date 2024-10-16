from web3 import AsyncWeb3
from web3.contract.async_contract import AsyncContract

from client import Client
from utils import get_json


class MagicEden:
    def __init__(self, client: Client):
        self.client = client
        self.sea_drop_address = '0x00005EA00Ac477B1030CE78506496e8C2dE24bf5'
        self.sea_drop_abi_path = (
            'data', 'abis', 'magic_eden', 'sea_drop_abi.json'
        )
        
    async def mint_reservoir_polygon_open_mint_2(self, quantity: int = 1) -> str:
        nft_address = AsyncWeb3.to_checksum_address(
            '0xf13e8fc5bfe323d8c5af3708d205500b994b3815'
        )
        sea_drop_contract: AsyncContract = self.client.w3.eth.contract(
            address=self.sea_drop_address,
            abi=get_json(self.sea_drop_abi_path)
        )

        [fee_recipient_contract] = await sea_drop_contract.functions.getAllowedFeeRecipients(
            nft_address
        ).call()

        data = sea_drop_contract.encodeABI(
            fn_name='mintPublic',
            args=(
                nft_address,
                fee_recipient_contract,
                self.client.account.address,
                quantity
            )
        )

        tx_hash_bytes = await self.client.send_transaction(
            to=sea_drop_contract.address,
            data=data
        )
        receipt = await self.client.w3.eth.wait_for_transaction_receipt(
            tx_hash_bytes
        )

        return tx_hash_bytes.hex() if receipt else 'Failed mint'

    async def mint(self, nft_address: str, quantity: int = 1) -> str:
        nft_address = AsyncWeb3.to_checksum_address(nft_address)
        sea_drop_contract: AsyncContract = self.client.w3.eth.contract(
            address=self.sea_drop_address,
            abi=get_json(self.sea_drop_abi_path)
        )

        [fee_recipient_contract] = await sea_drop_contract.functions.getAllowedFeeRecipients(
            nft_address
        ).call()

        data = sea_drop_contract.encodeABI(
            fn_name='mintPublic',
            args=(
                nft_address,
                fee_recipient_contract,
                self.client.account.address,
                quantity
            )
        )

        tx_hash_bytes = await self.client.send_transaction(
            to=sea_drop_contract.address,
            data=data
        )
        receipt = await self.client.w3.eth.wait_for_transaction_receipt(
            tx_hash_bytes
        )

        return tx_hash_bytes.hex() if receipt else 'Failed mint'

    async def mint_reservoir_polygon_open_mint_2(self, quantity: int = 1) -> str:
        return await self.mint(
            nft_address='0xf13e8fc5bfe323d8c5af3708d205500b994b3815',
            quantity=quantity
        )