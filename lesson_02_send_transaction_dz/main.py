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
    
    ## №1    
    # print(await whale_nft.mint())
    
    ## №2
    # print(await magic_eden.mint_oxygen_capsule_nft())
    
    ## №3
    # print(await quickswap.swap_native_to_token(
    #     native_amount=5, 
    #     token_name='USDC', 
    #     slippage=1.5)
    # )
    # print('Sleep after swap 15 secs...')
    # await asyncio.sleep(15)
    # print(await quickswap.swap_token_to_native(
    #     token_name='USDC', 
    #     amount=1.8, 
    #     slippage=1.5
    # ))
    
    ## №4
    # print(await quickswap.swap(
    #     from_token_name='USDC',
    #     to_token_name='POL',
    #     amount=2.642942,
    #     slippage=1
    # ))
    
    # №5
    # print(await magic_eden.mint_oxygen_nft('0x81309077AB508b2BFA19C8160EBaac9048320F1c'))
    # await asyncio.sleep(10)
    # print(await magic_eden.mint_oxygen_nft('0x4bB514EbF031a7f47dA9C5eaB74d6763B14DC78c'))


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())