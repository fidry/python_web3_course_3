import asyncio
import random
import time

from eth_abi import abi
from web3 import AsyncWeb3
from web3.contract import AsyncContract

from client import Client
from data.models import (
    TokenAmount,
    Tokens,
    ABIs,
    SyncSwapFullAbi,
)


class SyncSwap:
    def __init__(self, client: Client):
        self.client = client

    async def _get_raw_tx_params(self, wei_value: float = 0) -> dict:
        return {
            "chainId": await self.client.w3.eth.chain_id,
            "from": self.client.account.address,
            "value": wei_value,
            "gasPrice": await self.client.w3.eth.gas_price,
            "nonce": await self.client.w3.eth.get_transaction_count(self.client.account.address),
        }

    async def _approve_token_if_needed(
        self,
        token_contract: AsyncContract,
        router_address: str,
        token_amount: TokenAmount,
        is_unlimited: bool = False
    ):
        allowance, token_symbol = await asyncio.gather(
            token_contract.functions.allowance(
                self.client.account.address,
                router_address
            ).call(),
            token_contract.functions.symbol().call()
        )

        if token_amount.Wei <= allowance:
            return
        
        token_amount_wei = (
            2 ** 256 - 1 
            if is_unlimited
            else token_amount.Wei
        )
        token_amount_msg = (
            f'unlimited {token_symbol}'
            if is_unlimited
            else f'{token_amount.Ether} {token_symbol}'
        )

        approve_tx_hash_bytes = await self.client.send_transaction(
            to=token_contract.address,
            data=token_contract.encodeABI(
                'approve',
                args=(router_address, token_amount_wei)
            ),
            max_priority_fee_per_gas=0
        )
        if approve_tx_hash_bytes:
            try:
                await self.client.verif_tx(tx_hash=approve_tx_hash_bytes)
                waiting_time = round(random.choice([1, 5]), 2)
                print(
                    f'Approved {token_amount_msg} to swap on SyncSwap, '
                    f'sleeping {waiting_time} secs...'
                )
                await asyncio.sleep(waiting_time)
            except Exception as err:
                print(
                    f'Approve transaction error!! tx_hash: '
                    f'{approve_tx_hash_bytes.hex()}; error: {err}'
                )
        else:
            print('Failed approve transaction')

    async def swap_usdc_e_to_eth(
        self,
        token_amount: TokenAmount | None = None,
        slippage: float = 0.5,
        is_all_balance: bool = False,
    ) -> str:
        """
        Function signature: 0x7b2151e5
        000: 0000000000000000000000000000000000000000000000000000000000000120
        020: 00000000000000000000000000000000000000000000000000037ffdfb3a5842 - 985_153_748_490_306 (amountOutMin)
        040: 000000000000000000000000000000000000000000000000000000006734f8a1 - deadline(int(time.time() + 3 hours))
        060: 0000000000000000000000003355df6d4c9c3035724fd0e3914de96a5a83aaf4 - USDC.e
        080: ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff - amountPermit
        0a0: 000000000000000000000000000000000000000000000000000000006734f88b - deadline
        0c0: 000000000000000000000000000000000000000000000000000000000000001c - 28 (?)
        0e0: 487b3565872c99a82016d110ea112a85af0bf1c8ea871b9c2f2baec8665b4c99 - permit
        100: 62cd3ec837687ed58d39926a6513dbc7125717bfd519e9025b661043b70ef9a3
        120: 0000000000000000000000000000000000000000000000000000000000000001
        140: 0000000000000000000000000000000000000000000000000000000000000020
        160: 0000000000000000000000000000000000000000000000000000000000000060
        180: 0000000000000000000000003355df6d4c9c3035724fd0e3914de96a5a83aaf4 - USDC.e
        1a0: 0000000000000000000000000000000000000000000000000000000000323473 - amountIn (3_290_227)
        1c0: 0000000000000000000000000000000000000000000000000000000000000003
        1e0: 0000000000000000000000000000000000000000000000000000000000000060
        200: 00000000000000000000000000000000000000000000000000000000000001a0
        220: 00000000000000000000000000000000000000000000000000000000000002e0
        240: 000000000000000000000000a65349507212f9d1df0b001e221ceb78ff23b155 - USDC.e/USDT LP
        260: 00000000000000000000000000000000000000000000000000000000000000a0
        280: 0000000000000000000000000000000000000000000000000000000000000000
        2a0: 0000000000000000000000000000000000000000000000000000000000000120
        2c0: 0000000000000000000000000000000000000000000000000000000000000000
        2e0: 0000000000000000000000000000000000000000000000000000000000000060
        300: 0000000000000000000000003355df6d4c9c3035724fd0e3914de96a5a83aaf4 - USDC.e
        320: 000000000000000000000000c029c9569c51d24af555106951078b5b4e11894a - USDT/WBTC LP
        340: 0000000000000000000000000000000000000000000000000000000000000000
        360: 0000000000000000000000000000000000000000000000000000000000000000
        380: 000000000000000000000000c029c9569c51d24af555106951078b5b4e11894a - USDT/WBTC LP
        3a0: 00000000000000000000000000000000000000000000000000000000000000a0
        3c0: 0000000000000000000000000000000000000000000000000000000000000000
        3e0: 0000000000000000000000000000000000000000000000000000000000000120
        400: 0000000000000000000000000000000000000000000000000000000000000001
        420: 0000000000000000000000000000000000000000000000000000000000000060
        440: 000000000000000000000000493257fd37edb34451f62edf8d2a0c418852ba4c - USDT
        460: 000000000000000000000000b3479139e07568ba954c8a14d5a8b3466e35533d - WETH/WBTC LP
        480: 0000000000000000000000000000000000000000000000000000000000000000
        4a0: 0000000000000000000000000000000000000000000000000000000000000000
        4c0: 000000000000000000000000b3479139e07568ba954c8a14d5a8b3466e35533d - WETH/WBTC LP
        4e0: 00000000000000000000000000000000000000000000000000000000000000a0
        500: 0000000000000000000000000000000000000000000000000000000000000000
        520: 0000000000000000000000000000000000000000000000000000000000000120
        540: 0000000000000000000000000000000000000000000000000000000000000001
        560: 0000000000000000000000000000000000000000000000000000000000000060
        580: 000000000000000000000000bbeb516fb02a01611cbbe0453fe3c580d7281011 - WBTC
        5a0: 0000000000000000000000002f5844b8b5c03bbc48408bfda1340f5181643f53 - own address
        5c0: 0000000000000000000000000000000000000000000000000000000000000001
        5e0: 0000000000000000000000000000000000000000000000000000000000000000
        """
        from_token_contract = self.client.w3.eth.contract(
            address=Tokens.USDC_E,
            abi=ABIs.TokenABI
        )
        to_token_contract = self.client.w3.eth.contract(
            address=Tokens.WETH,
            abi=ABIs.TokenABI
        )
        from_token_symbol, to_token_symbol, to_token_decimals = await asyncio.gather(
            from_token_contract.functions.symbol().call(),
            to_token_contract.functions.symbol().call(),
            to_token_contract.functions.decimals().call()
        )

        router_contract = self.client.w3.eth.contract(
            address=AsyncWeb3.to_checksum_address(
                '0x9B5def958d0f3b6955cBEa4D5B7809b2fb26b059'),
            abi=SyncSwapFullAbi
        )
        from_token_price_dollar, to_token_price_dollar = await asyncio.gather(
            self.client.get_token_price(token_symbol=from_token_symbol),
            self.client.get_token_price(token_symbol=to_token_symbol)
        )

        if is_all_balance:
            from_token_balance, from_token_decimals = await asyncio.gather(
                from_token_contract.functions.balanceOf(
                    self.client.account.address).call(),
                from_token_contract.functions.decimals().call()
            )
            token_amount = TokenAmount(
                amount=from_token_balance,
                decimals=from_token_decimals,
                wei=True
            )
        
        deadline = int(time.time()) + 11850
        amount_out_min = TokenAmount(
            amount=(float(token_amount.Ether)
                * from_token_price_dollar
                / to_token_price_dollar
                * (100 - slippage) / 100
            ),
            decimals=to_token_decimals
        )

        await self._approve_token_if_needed(
            token_contract=from_token_contract,
            router_address=router_contract.address,
            token_amount=token_amount,
            is_unlimited=True
        )

        steps = [
            [
                Tokens.USDC_E_ZK_LP,
                self.client.w3.to_hex(
                    abi.encode(
                        ['address', 'address', 'uint8'],
                        [from_token_contract.address, Tokens.ZK_WETH_C_LP, 2]
                    )
                ),
                Tokens.ZERO,
                '0x',
                False
            ],
            [
                Tokens.ZK_WETH_C_LP,
                self.client.w3.to_hex(
                    abi.encode(
                        ['address', 'address', 'uint8'],
                        [Tokens.ZK, self.client.account.address, 1]
                    )
                ),
                Tokens.ZERO,
                '0x',
                False
            ]
        ]
        paths = [
            steps,
            from_token_contract.address,
            token_amount.Wei
        ]
        tx_params = await router_contract.functions.swap(
            [paths],
            amount_out_min.Wei,
            deadline
        ).build_transaction(await self._get_raw_tx_params())

        signed_tx = self.client.w3.eth.account.sign_transaction(
            tx_params, self.client.private_key
        )
        tx_hash_bytes = await self.client.w3.eth.send_raw_transaction(
            signed_tx.rawTransaction
        )

        if tx_hash_bytes:
            try:
                tx_hash = await self.client.verif_tx(tx_hash=tx_hash_bytes)
                print(
                    f'Transaction success ({token_amount.Ether} '
                    f'{from_token_symbol} -> {amount_out_min.Ether} '
                    f'{to_token_symbol})!! tx_hash: {tx_hash}'
                )
            except Exception as err:
                print(
                    f'Transaction error!! tx_hash: {tx_hash_bytes.hex()}; error: {err}')
        else:
            print(f'Transaction error!!')
