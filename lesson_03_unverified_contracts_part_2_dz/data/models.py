from decimal import Decimal

from web3 import AsyncWeb3


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


class Tokens:
    WETH = AsyncWeb3.to_checksum_address('0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91')
    USDC = AsyncWeb3.to_checksum_address('0x1d17CBcF0D6D143135aE902365D2E5e2A16538D4')
    USDC_E = AsyncWeb3.to_checksum_address('0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4')
    USDT = AsyncWeb3.to_checksum_address('0x493257fd37edb34451f62edf8d2a0c418852ba4c')
    STAR = AsyncWeb3.to_checksum_address('0x838A66F841DD5148475a8918db0732c239499a03')
    ETH = AsyncWeb3.to_checksum_address(f'0x{"".zfill(40)}')

    USDC_E_ZK_LP = AsyncWeb3.to_checksum_address('0x40b768de8b2e4ed83d982804cb2fcc53d2529be9')
    ZK_WETH_LP = AsyncWeb3.to_checksum_address('0x1a32a715b4ebef211bbf4baa414f563b25cc50c9')
    ZK = AsyncWeb3.to_checksum_address('0x5a7d6b2f92c77fad6ccabd7ee0624e64907eaf3e')
    ZERO = AsyncWeb3.to_checksum_address('0x0000000000000000000000000000000000000000')


class TxArgs:
    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)

    def list(self) -> list[...]:
        return list(self.__dict__.values())

    def tuple(self) -> tuple[str, ...]:
        return tuple(self.__dict__.values())


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

    SpaceFiABI = [
        {
            "constant": False,
            "inputs": [
                {
                    "name": "amountOutMin",
                    "type": "uint256"
                },
                {
                    "name": "path",
                    "type": "address[]"
                },
                {
                    "name": "to",
                    "type": "address"
                },
                {
                    "name": "deadline",
                    "type": "uint256"
                }
            ],
            "name": "swapExactETHForTokens",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256[]"
                }
            ],
            "payable": True,
            "stateMutability": "payable",
            "type": "function"
        }
    ]

    SpaceFiABIBytes = [
        {
            "constant": False,
            "inputs": [
                {
                    "name": "",
                    "type": "uint256"
                },
                {
                    "name": "",
                    "type": "address[]"
                },
                {
                    "name": "",
                    "type": "address"
                },
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "name": "swap",
            "outputs": [],
            "payable": True,
            "stateMutability": "payable",
            "type": "function"
        }
    ]

    KoiFinance = [
        {
            "constant": False,
            "inputs": [
                {
                    "name": "commands",
                    "type": "bytes"
                },
                {
                    "name": "inputs",
                    "type": "bytes[]"
                },
                {
                    "name": "deadline",
                    "type": "uint256"
                }
            ],
            "name": "execute",
            "outputs": [],
            "payable": True,
            "stateMutability": "payable",
            "type": "function"
        }
    ]

    MavericABI = [
        {
            "constant": False,
            "inputs": [
                {
                    "components": [
                        {
                            "name": "path",
                            "type": "bytes"
                        },
                        {
                            "name": "wallet",
                            "type": "address"
                        },
                        {
                            "name": "deadline",
                            "type": "uint256"
                        },
                        {
                            "name": "amountIn",
                            "type": "uint256"
                        },
                        {
                            "name": "amountOut",
                            "type": "uint256"
                        },
                    ],
                    "name": "params",
                    "type": "tuple"
                }
            ],
            "name": "exactInput",
            "outputs": [],
            "payable": True,
            "stateMutability": "payable",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "refundETH",
            "outputs": [],
            "stateMutability": "payable",
            "type": "function"
        },
        {
            "inputs": [
                {
                    "name": "data",
                    "type": "bytes[]"
                }
            ],
            "name": "multicall",
            "outputs": [],
            "stateMutability": "payable",
            "type": "function"
        }
    ]

    SyncSwapABI = [
        {
            "inputs": [
                {
                    "components": [
                        {
                            "components": [
                                {
                                    "internalType": "address",
                                    "name": "pool",
                                    "type": "address"
                                },
                                {
                                    "internalType": "bytes",
                                    "name": "data",
                                    "type": "bytes"
                                },
                                {
                                    "internalType": "address",
                                    "name": "callback",
                                    "type": "address"
                                },
                                {
                                    "internalType": "bytes",
                                    "name": "callbackData",
                                    "type": "bytes"
                                },
                                {
                                    "name": "flag",
                                    "type": "bool"
                                }
                            ],
                            "internalType": "struct IRouter.SwapStep[]",
                            "name": "steps",
                            "type": "tuple[]"
                        },
                        {
                            "internalType": "address",
                            "name": "tokenIn",
                            "type": "address"
                        },
                        {
                            "internalType": "uint256",
                            "name": "amountIn",
                            "type": "uint256"
                        }
                    ],
                    "internalType": "struct IRouter.SwapPath[]",
                    "name": "paths",
                    "type": "tuple[]"
                },
                {
                    "internalType": "uint256",
                    "name": "amountOutMin",
                    "type": "uint256"
                },
                {
                    "internalType": "uint256",
                    "name": "deadline",
                    "type": "uint256"
                }
            ],
            "name": "swap",
            "outputs": [],
            "stateMutability": "payable",
            "type": "function"
        },
    ]