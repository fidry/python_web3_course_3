from web3 import AsyncWeb3
from web3.contract.async_contract import AsyncContract

from client import Client
from utils import get_json


class WhaleNft:
    MINT_ABI_PATH = ('data', 'abis', 'whale-app', 'mint_abi.json')
    MINT_ADDRESS_DICT = {
        'Polygon': '0xE1c907503B8d1545AFD5A89cc44FC1E538A132DA',
        'Arbitrum One': '0x26E9934024cdC7fcc9f390973d4D9ac1FA954a37'
    }
    
    def __init__(self, client: Client):
        self.client = client
    
    def get_mint_contract_by_network(self, network_name: str):
        if network_name not in self.MINT_ADDRESS_DICT:
            raise Exception(f'Network {network_name} not supported for mint')

        return AsyncWeb3.to_checksum_address(
            self.MINT_ADDRESS_DICT[network_name]
        )
    
    async def mint(self, network_name: str = 'Polygon') -> str:
        contract: AsyncContract = self.client.w3.eth.contract(
            address=self.get_mint_contract_by_network(network_name), 
            abi=get_json(self.MINT_ABI_PATH)
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
        
        return await self.client.verif_tx(tx_hash_bytes)