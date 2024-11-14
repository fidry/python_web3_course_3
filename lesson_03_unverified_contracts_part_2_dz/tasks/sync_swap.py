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
        Function signature: 0xd7570e45 - function selector/method ID
        000: 0000000000000000000000000000000000000000000000000000000000000060 - ссылка на следующую строку (000 + 60 = 060)
        020: 0000000000000000000000000000000000000000000000000001bf8b38d396b5 - 492_079_651_460_789 (amountOutMin)
        040: 000000000000000000000000000000000000000000000000000000006735fa7a - deadline
        060: 0000000000000000000000000000000000000000000000000000000000000001 - начало структуры
        080: 0000000000000000000000000000000000000000000000000000000000000020 - ссылка на следующую строку (080 + 20 = 0a0)
        0a0: 0000000000000000000000000000000000000000000000000000000000000060 - следующие 60(16) = 96(10) байтов = след. 3 строки
        0c0: 0000000000000000000000003355df6d4c9c3035724fd0e3914de96a5a83aaf4 - USDC.e - адрес входящего токена - 1 строка
        0e0: 0000000000000000000000000000000000000000000000000000000000186a4f - 1_600_079 (amountIn) - 2 строка
        100: 0000000000000000000000000000000000000000000000000000000000000002 - начало второй структуры - 3 строка
        120: 0000000000000000000000000000000000000000000000000000000000000040 - ссылка на вторую строку после этой
                                                                                (120(16) + 40(16) = 160(16))
        140: 0000000000000000000000000000000000000000000000000000000000000180 - 180(16) / 20(16) = 6 след строк
        160: 00000000000000000000000040b768de8b2e4ed83d982804cb2fcc53d2529be9 - USDC_E_ZK_LP
        180: 00000000000000000000000000000000000000000000000000000000000000a0 - 384(10) + 160(10) = 544(10) = 220(16)
                                                                                ccылка на 220 строку
        1a0: 0000000000000000000000000000000000000000000000000000000000000000 - 0x
        1c0: 0000000000000000000000000000000000000000000000000000000000000120 - 1c0(16) + 120(16) = 448 + 288 = 736(10) = 2E0(16)
        1e0: 0000000000000000000000000000000000000000000000000000000000000000
        200: 0000000000000000000000000000000000000000000000000000000000000060 - следующие 60(16) = 96(10) байтов = след. 3 строки
        220: 0000000000000000000000003355df6d4c9c3035724fd0e3914de96a5a83aaf4 - USDC.e - адрес входящего токена 
        240: 00000000000000000000000090899441d5c9801d57773a3d5b8b880520cf2fe1 - ZK_WETH_C_LP
        260: 0000000000000000000000000000000000000000000000000000000000000002 - const
        280: 0000000000000000000000000000000000000000000000000000000000000000 - zero address or 0x
        2a0: 00000000000000000000000090899441d5c9801d57773a3d5b8b880520cf2fe1 - ZK_WETH_C_LP
        2c0: 00000000000000000000000000000000000000000000000000000000000000a0 - 704(10) + 160(10) = 864(10) = 360(16)
                                                                                ccылка на 360 строку
        2e0: 0000000000000000000000000000000000000000000000000000000000000000 - zero address
        300: 0000000000000000000000000000000000000000000000000000000000000120 - 300(16) + 120(16) = 768 + 288 = 1056 = 420(16)
        320: 0000000000000000000000000000000000000000000000000000000000000000
        340: 0000000000000000000000000000000000000000000000000000000000000060 - следующие 60(16) = 96(10) байтов = след. 3 строки
        360: 0000000000000000000000005a7d6b2f92c77fad6ccabd7ee0624e64907eaf3e - ZK
        380: 0000000000000000000000002f5844b8b5c03bbc48408bfda1340f5181643f53 - my_address
        3a0: 0000000000000000000000000000000000000000000000000000000000000001 - const
        3c0: 0000000000000000000000000000000000000000000000000000000000000000 - zero_address
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
