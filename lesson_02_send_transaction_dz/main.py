import asyncio

import config
from client import Client
from tasks.magic_eden import MagicEden
from tasks.quick_swap import QuickSwap
from tasks.whale_nft import WhaleNft


async def main():
    client = Client(
        private_key=config.PRIVATE_KEY,
        rpc='https://polygon.llamarpc.com',
        proxy=config.PROXY
    )
    quickswap = QuickSwap(client)
    whale_nft = WhaleNft(client)
    magic_eden = MagicEden(client)
        
    # print(await whale_nft.mint())
    
    # print(await quickswap.swap_native_to_token(5, 'USDC', slippage=1.5))
    # print('Sleep after swap 15 secs...')
    # await asyncio.sleep(15)
    # print(await quickswap.swap_token_to_native('USDC', 1.8, slippage=1.5))
    
    # print(await magic_eden.mint_reservoir_polygon_open_mint(3))
    
    # print(await magic_eden.mint('0xf13e8fc5bfe323d8c5af3708d205500b994b3815'))


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())