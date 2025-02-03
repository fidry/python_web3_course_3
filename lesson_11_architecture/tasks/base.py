from client import Client
from data.models import TokenAmount
from utils.utils import randfloat

from data.models import Settings


class Base:
    def __init__(self, client: Client):
        self.client = client
        
    @staticmethod
    def to_cut_hex_prefix_and_zfill(data: int | str, length: int = 64):
        str_hex_data = str(data)
        """
        Convert the hex string to lowercase, remove the '0x' prefix, and fill it with zeros to the specified length.

        Args:
            hex_data (str): The original hex string.
            length (int): The desired length of the string after filling. The default is 64.

        Returns:
            str: The modified string with '0x' prefix removed and zero-filled to the specified length.
        """
        if str_hex_data.startswith('0x'):
            str_hex_data = str_hex_data[2:]

        return str_hex_data.zfill(length)
    

    # async def approve_interface(self, token_address, spender, amount: TokenAmount | None = None) -> bool:
    #     balance = await self.client.balance(token_address=token_address)
    #     if balance.Wei <= 0:
    #         return False
    #
    #     if not amount or amount.Wei > balance.Wei:
    #         amount = balance
    #
    #     approved = await self.client.transactions.approved_amount(
    #         token=token_address,
    #         spender=spender,
    #         owner=self.client.account.address
    #     )
    #
    #     if amount.Wei <= approved.Wei:
    #         return True
    #
    #     tx = await self.client.transactions.approve(
    #         token=token_address,
    #         spender=spender,
    #         amount=amount
    #     )
    #
    #     receipt = await tx.wait_for_receipt(client=self.client, timeout=300)
    #     if receipt:
    #         return True
    #
    #     return False
    #
    # async def get_token_info(self, contract_address):
    #     contract = await self.client.contracts.default_token(contract_address=contract_address)
    #     print('name:', await contract.functions.name().call())
    #     print('symbol:', await contract.functions.symbol().call())
    #     print('decimals:', await contract.functions.decimals().call())
    #
    # @staticmethod
    # def parse_params(params: str, has_function: bool = True):
    #     if has_function:
    #         function_signature = params[:10]
    #         print('function_signature', function_signature)
    #         params = params[10:]
    #     while params:
    #         print(params[:64])
    #         params = params[64:]
    #
    # @staticmethod
    # def get_eth_amount_for_swap():
    #     settings = Settings()
    #     return TokenAmount(
    #         amount=randfloat(
    #             from_=settings.eth_amount_for_swap.from_,
    #             to_=settings.eth_amount_for_swap.to_,
    #             step=0.0000001
    #         )
    #     )
