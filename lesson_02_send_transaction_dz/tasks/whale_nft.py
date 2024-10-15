from web3 import AsyncWeb3
from web3.contract.async_contract import AsyncContract

from client import Client
from utils import get_json


class WhaleNft:
    def __init__(self, client: Client):
        self.client = client
        self.mint_address_dict = {
            'Polygon': '0xE1c907503B8d1545AFD5A89cc44FC1E538A132DA',
            'Arbitrum One': '0x26E9934024cdC7fcc9f390973d4D9ac1FA954a37'
        }
        self.mint_abi = ('data', 'abis', 'whale-app', 'mint_abi.json')
    
    def get_mint_contract_by_network(self, network_name: str):
        if network_name not in self.mint_address_dict:
            raise Exception(f'Network {network_name} not supported for mint')

        return AsyncWeb3.to_checksum_address(
            self.mint_address_dict[network_name]
        )
            
    async def get_raw_tx_params(self, value: float = 0) -> dict:
        return {
            "chainId": await self.client.w3.eth.chain_id,
            "from": self.client.account.address,
            "value": value,
            "gasPrice": await self.client.w3.eth.gas_price,
            "nonce": await self.client.w3.eth.get_transaction_count(self.client.account.address),
        }
    
    async def mint(self, network_name: str = 'Polygon'):
        contract: AsyncContract = self.client.w3.eth.contract(
            address=self.get_mint_contract_by_network(network_name), 
            abi=get_json(self.mint_abi)
        )
        mint_price = await contract.functions.fee().call()
        
        data = contract.encodeABI(
            fn_name='mint',
            args=()
        )
        tx_hash_bytes = await self.client.send_transaction(
            to=contract.address,
            data=data,
            value=mint_price
        )
        receipt = await self.client.w3.eth.wait_for_transaction_receipt(tx_hash_bytes)
        
        return tx_hash_bytes.hex() if receipt['status'] else 'Failed'