import asyncio
from client import Client
import config
from data.models import TokenAmount
from tasks.koi_finance import KoiFinance


async def main():
    client = Client(
        private_key=config.PRIVATE_KEY,
        rpc='https://mainnet.era.zksync.io',
        proxy=config.PROXY
    )
    koi_finance = KoiFinance(client)
    await koi_finance.swap_eth_to_usdc(
        token_amount=TokenAmount(0.002),
        slippage=1
    )


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
