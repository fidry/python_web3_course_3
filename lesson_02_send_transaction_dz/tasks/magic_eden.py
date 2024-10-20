from web3 import AsyncWeb3
from web3.contract.async_contract import AsyncContract

from client import Client
from utils import get_json


class MagicEden:
    SEA_DROP_ADDRESS = '0x00005EA00Ac477B1030CE78506496e8C2dE24bf5'
    SEA_DROP_ABI_PATH = (
        'data', 'abis', 'magic_eden', 'sea_drop_abi.json'
    )
    OXYGEN_CAPSULE_ABI_PATH = (
        'data', 'abis', 'magic_eden', 'oxygen_capsule_abi.json'
    )
    
    def __init__(self, client: Client):
        self.client = client
        
    async def get_raw_tx_params(self, value: float = 0) -> dict:
        return {
            "chainId": await self.client.w3.eth.chain_id,
            "from": self.client.account.address,
            "value": value,
            "gasPrice": await self.client.w3.eth.gas_price,
            "nonce": await self.client.w3.eth.get_transaction_count(self.client.account.address),
        }
        
    async def mint_oxygen_capsule_nft(self):
        nft_address = AsyncWeb3.to_checksum_address(
            '0x4bB514EbF031a7f47dA9C5eaB74d6763B14DC78c'
        )
        oxygen_contract: AsyncContract = self.client.w3.eth.contract(
            address=nft_address,
            abi=get_json(self.OXYGEN_CAPSULE_ABI_PATH)
        )
        
        mint_price = await oxygen_contract.functions.MINT_PRICE().call()
        
        tx_params = await oxygen_contract.functions.safeMint(
            self.client.account.address
        ).build_transaction(
            await self.get_raw_tx_params(value=mint_price)
        )
        
        signed_tx = self.client.w3.eth.account.sign_transaction(tx_params, self.client.private_key)
        tx_hash_bytes = await self.client.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = await self.client.w3.eth.wait_for_transaction_receipt(tx_hash_bytes)
        
        return tx_hash_bytes.hex() if receipt['status'] else 'Failed'
    
    async def mint_oxygen_nft(self, address: str):
        nft_address = AsyncWeb3.to_checksum_address(
            address
        )
        oxygen_contract: AsyncContract = self.client.w3.eth.contract(
            address=nft_address,
            abi=get_json(self.OXYGEN_CAPSULE_ABI_PATH)
        )
        
        mint_price = await oxygen_contract.functions.MINT_PRICE().call()
        
        data = oxygen_contract.encodeABI(
            'safeMint',
            args=[self.client.account.address]
        )
        
        tx_params = await self.client.send_transaction(
            to=nft_address,
            data=data,
            value=mint_price
        )
        
        return await self.client.verif_tx(tx_params)
    
