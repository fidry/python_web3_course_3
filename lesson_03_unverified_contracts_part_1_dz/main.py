import asyncio
from client import Client
import config
from data.models import TokenAmount
from tasks.spacefi import SpaceFi
from tasks.spacefi_hard import SpaceFiHard


async def main():
    client = Client(
        private_key=config.PRIVATE_KEY,
        rpc='https://mainnet.era.zksync.io',
        proxy=config.PROXY
    )

    spacefi = SpaceFi(client)
    await spacefi.swap_eth_to_usdt(
        token_amount=TokenAmount(0.0006),
        slippage=5
    )
    await spacefi.swap_eth_to_wbtc(
        token_amount=TokenAmount(0.001),
        slippage=5
    )
    await spacefi.swap_usdt_to_usdc_e(
        slippage=5, 
        is_all_balance=True
    )
    await spacefi.swap_usdc_e_to_eth(
        token_amount=TokenAmount(2, decimals=6),
        slippage=5,
        is_all_balance=True
    )

    spacefi = SpaceFiHard(client)
    await spacefi.swap(
        from_token_symbol='WBTC',
        to_token_symbol='ETH',
        amount=0.00004,
        slippage=5
    )

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
