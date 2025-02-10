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


class ABIs:
    TokenABI = [
        {
            'constant': True,
            'inputs': [],
            'name': 'name',
            'outputs': [{'name': '', 'type': 'string'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [],
            'name': 'symbol',
            'outputs': [{'name': '', 'type': 'string'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [],
            'name': 'decimals',
            'outputs': [{'name': '', 'type': 'uint256'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [{'name': 'who', 'type': 'address'}],
            'name': 'balanceOf',
            'outputs': [{'name': '', 'type': 'uint256'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [
                {'name': 'spender', 'type': 'address'},
                {'name': 'amount', 'type': 'uint256'}
            ],
            'name': 'approve',
            'outputs': [],
            'payable': False,
            'stateMutability': 'nonpayable',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [
                {'name': 'owner', 'type': 'address'},
                {'name': 'spender', 'type': 'address'},
            ],
            'name': 'allowance',
            'outputs': [
                {'name': '', 'type': 'uint256'},
            ],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
    ]


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
    # routers
    SPACE_FI_ROUTER = RawContract(
        title='SpaceFi',
        address=AsyncWeb3.to_checksum_address('0xbE7D1FD1f6748bbDefC4fbaCafBb11C6Fc506d1d'),
        abi=read_json(path=(ABIS_DIR, 'space_fi', 'router_abi.json'))
    )

    KOI_FINANCE_ROUTER = RawContract(
        title='KoiFinance',
        address=AsyncWeb3.to_checksum_address('0x3388530FbaF0C916fA7C0390413DFB178Cb33CBb'),
        abi=read_json(path=(ABIS_DIR, 'koi_finance', 'router_abi.json'))
    )

    SYNCSWAP_ROUTER = RawContract(
        title='SyncSwap',
        address=AsyncWeb3.to_checksum_address('0x9B5def958d0f3b6955cBEa4D5B7809b2fb26b059'),
        abi=read_json(path=(ABIS_DIR, 'syncswap', 'router_abi.json'))
    )

    WHALE_NFT_ROUTER = RawContract(
        title='WhaleNFT',
        address=AsyncWeb3.to_checksum_address('0xF09A71F6CC8DE983dD58Ca474cBC33de43DDEBa9'),
        abi=read_json(path=(ABIS_DIR, 'whale-app', 'mint_abi.json'))
    )

    # tokens
    ZERO_ADDRESS = RawContract(
        title='Zero Address (ETH)',
        address=AsyncWeb3.to_checksum_address('0x0000000000000000000000000000000000000000'),
        abi=ABIs.TokenABI
    )

    WETH = RawContract(
        title='WETH',
        address=AsyncWeb3.to_checksum_address('0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91'),
        abi=ABIs.TokenABI
    )

    USDT = RawContract(
        title='USDT',
        address=AsyncWeb3.to_checksum_address('0x493257fD37EDB34451f62EDf8D2a0C418852bA4C'),
        abi=ABIs.TokenABI
    )

    USDC = RawContract(
        title='USDC',
        address=AsyncWeb3.to_checksum_address('0x1d17CBcF0D6D143135aE902365D2E5e2A16538D4'),
        abi=ABIs.TokenABI
    )

    USDC_E = RawContract(
        title='USDC.e',
        address=AsyncWeb3.to_checksum_address('0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4'),
        abi=ABIs.TokenABI
    )

    WBTC = RawContract(
        title='WBTC',
        address=AsyncWeb3.to_checksum_address('0xBBeB516fb02a01611cBBE0453Fe3c580D7281011'),
        abi=ABIs.TokenABI
    )

    SPACE = RawContract(
        title='SPACE',
        address=AsyncWeb3.to_checksum_address('0x47260090cE5e83454d5f05A0AbbB2C953835f777'),
        abi=ABIs.TokenABI
    )
    
    USDC_E_ZK_LP = RawContract(
        title='USDC_E_ZK_LP',
        address=AsyncWeb3.to_checksum_address('0x40b768de8b2e4ed83d982804cb2fcc53d2529be9'),
        abi=ABIs.TokenABI
    )
    
    ZK = RawContract(
        title='ZK',
        address=AsyncWeb3.to_checksum_address('0x5a7d6b2f92c77fad6ccabd7ee0624e64907eaf3e'),
        abi=ABIs.TokenABI
    )
    
    ZK_WETH_C_LP = RawContract(
        title='ZK_WETH_C_LP',
        address=AsyncWeb3.to_checksum_address('0x90899441D5c9801d57773a3d5b8B880520CF2fe1'),
        abi=ABIs.TokenABI
    )
