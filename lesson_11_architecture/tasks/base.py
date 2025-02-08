from web3.types import ChecksumAddress

from client import Client
from data.models import TokenAmount
from utils.utils import randfloat
from data.models import Settings


class Base:
    def __init__(self, client: Client):
        self.client = client
        
    @staticmethod
    def to_cut_hex_prefix_and_zfill(data: int | str, length: int = 64):
        """
        Convert the hex string to lowercase, remove the '0x' prefix, and fill it with zeros to the specified length.

        Args:
            data (str): The original hex string.
            length (int): The desired length of the string after filling. The default is 64.

        Returns:
            str: The modified string with '0x' prefix removed and zero-filled to the specified length.
        """
        str_hex_data = str(data)

        if str_hex_data.startswith('0x'):
            str_hex_data = str_hex_data[2:]

        return str_hex_data.zfill(length)

    @staticmethod
    def get_eth_amount_for_swap():
        settings = Settings()
        return TokenAmount(
            amount=randfloat(
                from_=settings.eth_amount_for_swap.from_,
                to_=settings.eth_amount_for_swap.to_,
                decimal_places=7
            )
        )

    async def approve_interface(
            self,
            token_address: str | ChecksumAddress,
            spender: str | ChecksumAddress,
            amount: TokenAmount | None = None
    ) -> bool:
        balance = await self.client.balance(token_address=token_address)
        if balance.Wei <= 0:
            return False

        if not amount or amount.Wei > balance.Wei:
            amount = balance

        approved = await self.client.approved_amount(
            token_address=token_address,
            spender=spender,
            owner=self.client.account.address
        )

        if amount.Wei <= approved.Wei:
            return True

        tx = await self.client.approve(
            token_address=token_address,
            spender=spender,
            amount=amount
        )

        if tx:
            return True
        return False
