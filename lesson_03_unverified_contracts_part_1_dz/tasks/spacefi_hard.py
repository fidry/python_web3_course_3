import asyncio
import time
from web3 import AsyncWeb3
from client import Client
from data.models import ABIs, TokenAmount

ZKSYNC_TOKENS_DICT = {
    # 'WETH': '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91',
    'WBTC': '0xBBeB516fb02a01611cBBE0453Fe3c580D7281011',
    'USDT': '0x493257fD37EDB34451f62EDf8D2a0C418852bA4C',
    'USDC': '0x1d17CBcF0D6D143135aE902365D2E5e2A16538D4',
    'USDC.E': '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4',
}

SPACEFI_PATHS = {
    ('ETH', 'USDT'): [
        '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91', # WETH
        '0x47260090cE5e83454d5f05A0AbbB2C953835f777', # SPACE
        '0x493257fD37EDB34451f62EDf8D2a0C418852bA4C'  # USDT
    ],
    ('ETH', 'USDC'): [
        '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91', # WETH
        '0x1d17CBcF0D6D143135aE902365D2E5e2A16538D4'  # USDC
    ],
    ('ETH', 'WBTC'): [
        '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91', # WETH
        '0xBBeB516fb02a01611cBBE0453Fe3c580D7281011'  # WBTC
    ],
    ('USDT', 'ETH'): [
        '0x493257fD37EDB34451f62EDf8D2a0C418852bA4C', # USDT
        '0x47260090cE5e83454d5f05A0AbbB2C953835f777', # SPACE
        '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91'  # WETH
    ],
    ('USDC.E', 'ETH'): [
        '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4', # USDC.E
        '0x47260090cE5e83454d5f05A0AbbB2C953835f777', # SPACE
        '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91'  # WETH
    ],
    ('USDC', 'USDT'): [
        '0x1d17CBcF0D6D143135aE902365D2E5e2A16538D4', # USDC
        '0x47260090cE5e83454d5f05A0AbbB2C953835f777', # SPACE
        '0x493257fD37EDB34451f62EDf8D2a0C418852bA4C', # USDT
    ],
    ('USDT', 'USDC.E'): [
        '0x493257fD37EDB34451f62EDf8D2a0C418852bA4C', # USDT
        '0x47260090cE5e83454d5f05A0AbbB2C953835f777', # SPACE
        '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4', # USDC
    ],
    ('WBTC', 'ETH'): [
        '0xBBeB516fb02a01611cBBE0453Fe3c580D7281011', # WBTC
        '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4', # USDC
        '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91'  # WETH
    ]
}

class SpaceFiHard:
    def __init__(self, client: Client):
        self.client = client

    async def get_raw_tx_params(self, wei_value: float = 0) -> dict:
        return {
            "chainId": await self.client.w3.eth.chain_id,
            "from": self.client.account.address,
            "value": wei_value,
            "gasPrice": await self.client.w3.eth.gas_price,
            "nonce": await self.client.w3.eth.get_transaction_count(self.client.account.address),
        }

    async def swap(
        self,
        from_token_symbol: str,
        to_token_symbol: str,
        amount: float,
        slippage: float = 0.5
    ):
        from_token_symbol = from_token_symbol.upper()
        to_token_symbol = to_token_symbol.upper()

        if from_token_symbol == to_token_symbol:
            print(f'Invalid input params: {from_token_symbol} -> {to_token_symbol}')
            return

        router_address = AsyncWeb3.to_checksum_address('0xbE7D1FD1f6748bbDefC4fbaCafBb11C6Fc506d1d')
        router_contract = self.client.w3.eth.contract(
            address=router_address,
            abi=ABIs.SpaceFiABI
        )

        if from_token_symbol != 'ETH':
            from_token_contract = self.client.w3.eth.contract(
                address=AsyncWeb3.to_checksum_address(ZKSYNC_TOKENS_DICT[from_token_symbol]),
                abi=ABIs.TokenABI
            )
            from_token_decimals = await from_token_contract.functions.decimals().call()
        else:
            from_token_decimals = 18
        
        if to_token_symbol != 'ETH':
            to_token_contract = self.client.w3.eth.contract(
                address=AsyncWeb3.to_checksum_address(ZKSYNC_TOKENS_DICT[to_token_symbol]),
                abi=ABIs.TokenABI
            )
            to_token_decimals = await to_token_contract.functions.decimals().call()
        else:
            to_token_decimals = 18

        amount_in = TokenAmount(
            amount=amount,
            decimals=from_token_decimals
        )

        from_token_price_dollar = await self.client.get_token_price(token_symbol=from_token_symbol)
        to_token_price_dollar = await self.client.get_token_price(token_symbol=to_token_symbol)

        amount_out_min = TokenAmount(
            amount=(float(amount_in.Ether) 
                * from_token_price_dollar 
                / to_token_price_dollar 
                * (100 - slippage) / 100),
            decimals=to_token_decimals
        )

        # list comprehension
        checksum_path = [
            AsyncWeb3.to_checksum_address(path_part) 
            for path_part in SPACEFI_PATHS[(from_token_symbol, to_token_symbol)]
        ]
        args_list = [
            amount_out_min.Wei,
            checksum_path,
            self.client.account.address,
            int(time.time() + 1200)
        ]

        value = 0
        if from_token_symbol != 'ETH':
            args_list.insert(0, amount_in.Wei)

            approve = await self.client.send_transaction(
                to=from_token_contract.address,
                data=from_token_contract.encodeABI(
                    'approve',
                    args=(router_address, amount_in.Wei)
                ),
                max_priority_fee_per_gas=0
            )

            approve_tx_hash = await self.client.verif_tx(approve)
        
            if approve_tx_hash:
                waiting_time = 15
                print(
                    f'Approved {amount_in.Ether} {from_token_symbol} to swap on SpaceFi, '
                    f'sleeping {waiting_time} secs...'
                )
                await asyncio.sleep(waiting_time)
            else:
                print('Failed')
        else:
            value = amount_in.Wei

        method_name = ( 
            'swapExactTokensForETH' 
            if from_token_symbol != 'ETH' 
            else 'swapExactETHForTokens'
        )

        data=router_contract.encodeABI(
            method_name,
            args=tuple(args_list)
        )
        tx_hash_bytes = await self.client.send_transaction(
            to=router_address,
            data=data,
            value=value,
            max_priority_fee_per_gas=0
        )
        
        if tx_hash_bytes:
            try:
                tx_hash = await self.client.verif_tx(tx_hash=tx_hash_bytes)
                print(f'Transaction success ({amount_in.Ether} {from_token_symbol} -> {amount_out_min.Ether} {to_token_symbol})!! '
                    f'tx_hash: {tx_hash}')
                # Transaction success (0.001 ETH -> 2.7496135 USDT)!! tx_hash: 0x4a932d2340742a921ab9d2c52d65ab38671cd8f707a2497439d6ec5b5cec602f
                # Transaction success (0.87 USDT -> 0.0002914421881475342 ETH)!! tx_hash: 0x8e505d335bfe54f961848bbb961f15aa84b51ccbcc283156476c01b470a42d1b
                # Transaction success (2.0 USDT -> 0.000621587742289722 ETH)!! tx_hash: 0xdaae5af02bfa7c2a0922d88840a535d027f56b16b48e5a7cdebb9f4616ef3d2c
                # Transaction success (0.0008 ETH -> 0.000029105322888639857 WBTC)!! tx_hash: 0x669310c1ec16ed385e8d0778cc96c05e2bc3d8b2e6d3490f4363b370bc6d2446
                # Transaction success (0.00003 WBTC -> 0.0007439477656330048 ETH)!! tx_hash: 0x5879c726265b08d2c62424401ca4b03b89e4eef249f0d40983f05b3a24a872af
            except Exception as err:
                print(f'Transaction error!! tx_hash: {tx_hash_bytes.hex()}; error: {err}')
        else:
            print(f'Transaction error!!')