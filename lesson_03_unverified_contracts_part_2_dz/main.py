import asyncio
from client import Client
import config
from data.models import TokenAmount
from tasks.koi_finance import KoiFinance
from tasks.maverick import Maverick
from tasks.sync_swap import SyncSwap


async def main():
    client = Client(
        private_key=config.PRIVATE_KEY,
        rpc='https://mainnet.era.zksync.io',
        proxy=config.PROXY
    )
    koi_finance = KoiFinance(client)
    await koi_finance.swap_eth_to_usdc(
        token_amount=TokenAmount(0.001),
        slippage=1
    )
    maverick = Maverick(client)
    await maverick.swap_usdc_to_mav(
        slippage=1,
        is_all_balance=True
    )
    sync_swap = SyncSwap(client)
    await sync_swap.swap_usdc_e_to_eth(
        slippage=1,
        is_all_balance=True
    )


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
