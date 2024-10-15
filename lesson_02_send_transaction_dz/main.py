import asyncio

import config
from client import Client
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
    
    # print(await quickswap.swap_native_to_token(5, 'USDC'))
    
    # print('Sleep after swap 15 secs...')
    # asyncio.sleep(15)
    # print(await quickswap.swap_token_to_native('USDC', 2.14))
    
    print(await whale_nft.mint())


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())