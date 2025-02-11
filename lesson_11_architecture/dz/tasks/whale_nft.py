from web3 import AsyncWeb3
from web3.contract.async_contract import AsyncContract

from client import Client
from tasks.base import Base
from data.config import logger
from data.models import Contracts


class WhaleNft(Base):
    MINT_ADDRESS_DICT = {
        # 'Polygon': '0xE1c907503B8d1545AFD5A89cc44FC1E538A132DA',
        # 'Arbitrum One': '0x26E9934024cdC7fcc9f390973d4D9ac1FA954a37',
        'zkSync Era': Contracts.WHALE_NFT_ROUTER.address
    }
    
    def get_mint_contract_by_network(self, network_name: str):
        if network_name not in self.MINT_ADDRESS_DICT:
            raise Exception(f'Network {network_name} not supported for mint')

        return AsyncWeb3.to_checksum_address(
            self.MINT_ADDRESS_DICT[network_name]
        )
    
    async def mint(self, network_name: str = 'zkSync Era') -> str:
        router = Contracts.WHALE_NFT_ROUTER
        failed_text = f'Failed to mint NFT via {router.title}'
        logger.info(f'Start mint NFT via {router.title}')

        contract: AsyncContract = self.client.w3.eth.contract(
            address=self.get_mint_contract_by_network(network_name), 
            abi=router.abi
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

        if not tx_hash_bytes:
            return f'{failed_text} | Can not get tx_hash_bytes'

        try:
            tx_hash = await self.client.verif_tx(tx_hash=tx_hash_bytes)
            return (f'({router.title}) Transaction success! NFT minted via {router.title} | '
                    f'tx_hash: {tx_hash}')
        except Exception as err:
            return f' {failed_text} | tx_hash: {tx_hash_bytes.hex()}; error: {err}'
