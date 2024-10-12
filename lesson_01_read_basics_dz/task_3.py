import asyncio
import json

from web3 import AsyncWeb3

def read_json(path: str):
    return json.load(open(path))
    
async def main():
    rpc = 'https://ethereum-rpc.publicnode.com'
    w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc))
    
    nft_address = AsyncWeb3.to_checksum_address('0x932261f9Fc8DA46C4a22e31B45c4De60623848bF')
    nft_abi = read_json('data/nft_abi.json')
    
    nft_contract = w3.eth.contract(nft_address, abi=nft_abi)
    
    nft_name = await nft_contract.functions.name().call()
    symbol = await nft_contract.functions.symbol().call()
    top_holder_balance = await nft_contract.functions.balanceOf('0x5a7749f83b81B301cAb5f48EB8516B986DAef23D').call()
    owner = await nft_contract.functions.owner().call()
    is_paused = await nft_contract.functions.paused().call()
    
    print('Name:', nft_name)
    print('Symbol:', symbol)
    print('Top minter has NFT(s):',top_holder_balance)
    print('Owner:', owner)
    print('Is mint paused:', is_paused)

if __name__ == '__main__':
    asyncio.run(main())