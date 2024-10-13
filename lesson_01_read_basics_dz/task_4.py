import asyncio
import json

from web3 import AsyncWeb3

def read_json(path: str):
    return json.load(open(path))
    
async def main():
    nft_addresses = [
        '0xc94025c2eA9512857BD8E1e611aB9b773b769350',
        '0xD43A183C97dB9174962607A8b6552CE320eAc5aA',
        '0xee0d4a8f649d83f6ba5e5c9e6c4d4f6ae846846a',
    ]
    
    rpc = 'https://1rpc.io/zksync2-era'
    w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc))
    
    token_abi = read_json('data/erc_20_abi.json')
    
    for address in nft_addresses:
        address = AsyncWeb3.to_checksum_address(address)
        
        nft_contract = w3.eth.contract(address, abi=token_abi)
        print('Name:', await nft_contract.functions.name().call())
        print('Symbol:', await nft_contract.functions.symbol().call())
        try:
            decimals = await nft_contract.functions.decimals().call()
            print(f'Decimals: {decimals}\n')
        except Exception as e:
            print(f'{e}\n')

if __name__ == '__main__':
    asyncio.run(main())