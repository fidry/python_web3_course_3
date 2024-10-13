import asyncio
import json

from web3 import AsyncWeb3
from web3.types import Wei

def read_json(path: str):
    return json.load(open(path))
    
async def main():
    addresses = [
        '0x95222290DD7278Aa3Ddd389Cc1E1d165CC4BAfe5',
        '0x930fe9071bad747449d5d3d79c516d873925ca78',
        '0xa1C68165734b5dC40B9543D3c16a58c2D38D2BF7',
        '0x1370a6B86a73B5e3A2629be2D7ca27D379eaa3E0',
        '0xB9b64404ABe22bC7722EedBF512805933F2069E0',
        '0x0d2237Fd78538B7829Be568aeBF44b07d670B386',
        '0x24FB6523036EBCb3cc51DEFF138066DCcf6Bed0f',
        '0x5BCbdfB6cc624b959c39A2D16110D1f2D9204F72',
        '0xdf542aCB6fB3146b4938F03ddD9788F7B36E5170',
        '0x62f73147C41C21A4B57dac3752b054C72816FE02',
        '0xE5117e3eA2b1d87e8f9dc5FE1102Db9434Fe827E'
    ]
    
    rpc = 'https://ethereum-rpc.publicnode.com'
    w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc))
    
    usdt_address = '0xdAC17F958D2ee523a2206206994597C13D831ec7'
    # usdt_address = AsyncWeb3.to_checksum_address('0xdac17f958d2ee523a2206206994597c13d831ec7')
    token_abi = read_json('data/erc_20_abi.json')
    
    token_contract = w3.eth.contract(address=usdt_address, abi=token_abi)
    decimals = await token_contract.functions.decimals().call() # 10 ** -6 
    balances_dict = {}
    
    for address in addresses:
        address = AsyncWeb3.to_checksum_address(address)
        balance: Wei = await token_contract.functions.balanceOf(address).call()
        balances_dict.update({
            address: balance / 10 ** decimals
        })
        # 1 ETH, decimals = 18
        # 1 ETH = 10 ** 18 Wei
        # 1 USDT, decimals = 6
        # 1 USDT = 10 ** 6 Wei
            
    sorted_balances = {k: v for k, v in sorted(
        balances_dict.items(), key=lambda item: item[1], reverse=True)
    }
    for address, balance in sorted_balances.items():
        print(address,'|',balance)    

if __name__ == '__main__':
    asyncio.run(main())