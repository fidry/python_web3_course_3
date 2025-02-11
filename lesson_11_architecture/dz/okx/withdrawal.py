from loguru import logger
from eth_typing import ChecksumAddress

from utils.utils import randfloat
from okx.okx_actions import OKXActions
from data.models import Settings, TokenAmount


async def okx_withdraw_evm(
        chain: str,
        token_symbol: str,
        wallet_address: str | ChecksumAddress,
        amount_to_withdraw: TokenAmount | None = None,
) -> str:
    settings = Settings()

    if not settings.okx.credentials.completely_filled():
        return 'Failed to withdraw from OKX (OKX credentials not filled)'

    if not amount_to_withdraw:
        amount_to_withdraw = TokenAmount(
            amount=randfloat(
                from_=settings.okx.withdraw_amount.from_,
                to_=settings.okx.withdraw_amount.to_,
                decimal_places=8
            ),
            decimals=18
        )

    okx = OKXActions(credentials=settings.okx.credentials)

    logger.info(f'Start to withdraw {amount_to_withdraw} {token_symbol} ({chain}) to {wallet_address}')

    return await okx.withdraw(
        to_address=wallet_address,
        amount=str(amount_to_withdraw.Ether),
        token_symbol=token_symbol,
        chain=chain
    )
