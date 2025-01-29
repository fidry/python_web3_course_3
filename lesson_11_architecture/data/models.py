import json
from decimal import Decimal
from dataclasses import dataclass

from eth_typing import ChecksumAddress
from web3 import AsyncWeb3

# from libs.eth_async.data.models import RawContract, DefaultABIs
from py_okx_async.models import OKXCredentials
from utils.files_utils import read_json
from data.config import SETTINGS_FILE, ABIS_DIR


class TokenAmount:
    Wei: int
    Ether: Decimal
    decimals: int

    def __init__(self, amount: int | float | str | Decimal, decimals: int = 18, wei: bool = False) -> None:
        if wei:
            self.Wei: int = int(amount)
            self.Ether: Decimal = Decimal(str(amount)) / 10 ** decimals

        else:
            self.Wei: int = int(Decimal(str(amount)) * 10 ** decimals)
            self.Ether: Decimal = Decimal(str(amount))

        self.decimals = decimals

    def __str__(self):
        return f'{self.Wei}'


@dataclass
class WalletCSV:
    header = ['private_key', 'proxy', 'name', 'okx_address']

    def __init__(self, private_key: str, proxy: str = '', name: str = '', okx_address: str = ''):
        self.private_key = private_key
        self.proxy = proxy
        self.name = name
        self.okx_address = okx_address


@dataclass
class FromTo:
    from_: int | float
    to_: int | float


class OkxModel:
    allow_withdrawal_from_exchange: bool
    required_minimum_balance: float
    withdraw_amount: FromTo
    delay_between_withdrawals: FromTo
    credentials: OKXCredentials


class Settings:
    def __init__(self):
        json_data = read_json(path=SETTINGS_FILE)

        self.delay_in_case_of_error: int = json_data['delay_in_case_of_error']
        self.rpc_eth: str = json_data['rpc_eth']
        self.rpc_zksync: str = json_data['rpc_zksync']
        self.maximum_gas_price: int = json_data['maximum_gas_price']

        self.okx = OkxModel()
        self.okx.allow_withdrawal_from_exchange = json_data['okx']['allow_withdrawal_from_exchange']
        self.okx.required_minimum_balance = json_data['okx']['required_minimum_balance']
        self.okx.withdraw_amount = FromTo(
            from_=json_data['okx']['withdraw_amount']['from'],
            to_=json_data['okx']['withdraw_amount']['to'],
        )
        self.okx.delay_between_withdrawals = FromTo(
            from_=json_data['okx']['delay_between_withdrawals']['from'],
            to_=json_data['okx']['delay_between_withdrawals']['to'],
        )
        self.okx.credentials = OKXCredentials(
            api_key=json_data['okx']['credentials']['api_key'],
            secret_key=json_data['okx']['credentials']['secret_key'],
            passphrase=json_data['okx']['credentials']['passphrase']
        )

        self.oklink_api_key: str = json_data['oklink_api_key']
        self.minimal_balance: float = json_data['minimal_balance']

        self.number_of_swaps: FromTo = FromTo(
            from_=json_data['number_of_swaps']['from'], to_=json_data['number_of_swaps']['to'])
        self.number_of_mint_nft: FromTo = FromTo(
            from_=json_data['number_of_mint_nft']['from'], to_=json_data['number_of_mint_nft']['to'])

        self.initial_actions_delay: FromTo = FromTo(
            from_=json_data['initial_actions_delay']['from'], to_=json_data['initial_actions_delay']['to']
        )
        self.activity_actions_delay: FromTo = FromTo(
            from_=json_data['activity_actions_delay']['from'], to_=json_data['activity_actions_delay']['to']
        )

        self.eth_amount_for_swap: FromTo = FromTo(
            from_=json_data['eth_amount_for_swap']['from'], to_=json_data['eth_amount_for_swap']['to']
        )


class RawContract:
    """
    An instance of a raw contract.

    Attributes:
        title str: a contract title.
        address (ChecksumAddress): a contract address.
        abi list[dict[str, Any]] | str: an ABI of the contract.

    """
    title: str
    address: ChecksumAddress
    abi: list[dict[str, ...]]

    def __init__(self, address: str, abi: list[dict[str, ...]] | str | None = None, title: str = '') -> None:
        """
        Initialize the class.

        Args:
            title (str): a contract title.
            address (str): a contract address.
            abi (Union[List[Dict[str, Any]], str]): an ABI of the contract.

        """
        self.title = title
        self.address = AsyncWeb3.to_checksum_address(address)
        self.abi = json.loads(abi) if isinstance(abi, str) else abi

    def __eq__(self, other) -> bool:
        if self.address == other.address and self.abi == other.abi:
            return True
        return False


class Contracts:
    # ZkSync
    MUTE = RawContract(
        title='mute',
        address='0x8b791913eb07c32779a16750e3868aa8495f5964',
        abi=read_json(path=(ABIS_DIR, 'mute.json'))
    )

#     SPACE_FI = RawContract(
#         title='space_fi',
#         address='0xbe7d1fd1f6748bbdefc4fbacafbb11c6fc506d1d',
#         abi=read_json(path=(ABIS_DIR, 'space_fi.json'))
#     )
#
#     SYNC_SWAP = RawContract(
#         title='sync_swap',
#         address='0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295',
#         abi=read_json(path=(ABIS_DIR, 'sync_swap.json'))
#     )
#
#     MAVERICK = RawContract(
#         title='maverick',
#         address='0x39E098A153Ad69834a9Dac32f0FCa92066aD03f4',
#         abi=read_json(path=(ABIS_DIR, 'maverick.json'))
#     )
#
#     DMAIL = RawContract(
#         title='dmail',
#         address='0x981F198286E40F9979274E0876636E9144B8FB8E',
#         abi=read_json(path=(ABIS_DIR, 'dmail.json'))
#     )
#
#     WETH = RawContract(
#         title='WETH',
#         address='0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91',
#         abi=read_json(path=(ABIS_DIR, 'WETH.json'))
#     )
#
#     USDC = RawContract(
#         title='USDC',
#         address='0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4',
#         abi=DefaultABIs.Token
#     )
#
#     WBTC = RawContract(
#         title='WBTC',
#         address='0xBBeB516fb02a01611cBBE0453Fe3c580D7281011',
#         abi=DefaultABIs.Token
#     )
#
#     USDT = RawContract(
#         title='USDT',
#         address='0x493257fd37edb34451f62edf8d2a0c418852ba4c',
#         abi=DefaultABIs.Token
#     )
#
#     ceBUSD = RawContract(
#         title='ceBUSD',
#         address='0x2039bb4116B4EFc145Ec4f0e2eA75012D6C0f181',
#         abi=DefaultABIs.Token
#     )
