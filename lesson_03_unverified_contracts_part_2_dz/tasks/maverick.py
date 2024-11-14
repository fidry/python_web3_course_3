import asyncio
import random
import time

from web3 import AsyncWeb3
from web3.contract import AsyncContract

from client import Client
from data.models import ABIs, TokenAmount, Tokens


class Maverick:
    def __init__(self, client: Client):
        self.client = client

    async def _approve_token_if_needed(
        self,
        token_contract: AsyncContract,
        router_address: str,
        token_amount: TokenAmount,
    ):
        allowance, token_symbol = await asyncio.gather(
            token_contract.functions.allowance(
                self.client.account.address,
                router_address
            ).call(),
            token_contract.functions.symbol().call()
        )

        if allowance >= token_amount.Wei:
            return
        
        approve_tx_hash_bytes = await self.client.send_transaction(
            to=token_contract.address,
            data=token_contract.encodeABI(
                'approve',
                args=(router_address, token_amount.Wei)
            ),
            max_priority_fee_per_gas=0
        )
        if approve_tx_hash_bytes:
            try:
                await self.client.verif_tx(tx_hash=approve_tx_hash_bytes)
                waiting_time = round(random.choice([1, 5]), 2)
                print(
                    f'Approved {token_amount.Ether} {token_symbol} to swap on Maverick, '
                    f'sleeping {waiting_time} secs...'
                )
                await asyncio.sleep(waiting_time)
            except Exception as err:
                print(
                    f'Approve transaction error!! tx_hash: '
                    f'{approve_tx_hash_bytes.hex()}; error: {err}'
                )
        else:
            print('Failed')

    async def swap_usdc_to_eth(
        self,
        token_amount: TokenAmount,
        slippage: float = 1,
        is_all_balance: bool = False
    ):
        """
        Function signature: 0xc04b8d59 - exactInput((bytes,address,uint256,uint256,uint256))
        000: 0000000000000000000000000000000000000000000000000000000000000020 - ccылка на 20 байт
        020: 00000000000000000000000000000000000000000000000000000000000000a0 - размер структуры (160 байт), 
                                                                                160 / 32 = 5 - cлед 5 строк - это структура (tuple)
        040: 0000000000000000000000000000000000000000000000000000000000000000 - 0x00000...0000 address
        060: 0000000000000000000000000000000000000000000000000000000067349f69 - deadline (int(time.time() + 3 * 60))
        080: 000000000000000000000000000000000000000000000000000000000065f852 - amountIn (6_682_706 USDC)
        0a0: 00000000000000000000000000000000000000000000000000076bb11d5370a1 - amountOutMin (2_088_733_282_365_601 ETH)
        0c0: 0000000000000000000000000000000000000000000000000000000000000064 - размер массива байтов (100 байт), 100 / 5 = 20 bytes = 40 hexs
        0e0: 1d17cbcf0d6d143135ae902365d2e5e2a16538d4ef1cada686c12f7a0008cd5b - 1d17cbcf0d6d143135ae902365d2e5e2a16538d4 USDC
        100: 78eefaad35ad6f013355df6d4c9c3035724fd0e3914de96a5a83aaf4688ea0d0 - ef1cada686c12f7a0008cd5b78eefaad35ad6f01 pool USDC/USDC.e  
        120: 7acadd7d74ec7c729f1d0ca0dd4bb6655aea5775959fbc2557cc8789bc1bf90a - 3355df6d4c9c3035724fd0e3914de96a5a83aaf4 USDC.e
        140: 239d9a9100000000000000000000000000000000000000000000000000000000 - 688ea0d07acadd7d74ec7c729f1d0ca0dd4bb665 USDC.e/WETH
                                                                                5aea5775959fbc2557cc8789bc1bf90a239d9a91 WETH

        Function signature: 0x49404b7c - unwrapWETH9(uint256,address)
        000: 00000000000000000000000000000000000000000000000000076bb11d5370a1 - amountOutMin (2_088_733_282_365_601 ETH)
        020: 0000000000000000000000002f5844b8b5c03bbc48408bfda1340f5181643f53 - our address
        """
        path = [
            Tokens.USDC,
            'ef1cada686c12f7a0008cd5b78eefaad35ad6f01',  # pool USDC/USDC.e  
            Tokens.USDC_E,
            '688ea0d07acadd7d74ec7c729f1d0ca0dd4bb665',  # pool USDC.e/WETH
            Tokens.WETH,
        ]

        from_token_contract = self.client.w3.eth.contract(
            address=AsyncWeb3.to_checksum_address(path[0]),
            abi=ABIs.TokenABI
        )
        to_token_contract = self.client.w3.eth.contract(
            address=AsyncWeb3.to_checksum_address(path[-1]),
            abi=ABIs.TokenABI
        )
        router_contract = self.client.w3.eth.contract(
            address=AsyncWeb3.to_checksum_address('0x39E098A153Ad69834a9Dac32f0FCa92066aD03f4'),
            abi=ABIs.MaverickABI
        )

        from_token_symbol, to_token_decimals = await asyncio.gather(
            from_token_contract.functions.symbol().call(),
            to_token_contract.functions.decimals().call(),
        )

        if is_all_balance:
            from_token_balance, from_token_decimals = await asyncio.gather(
                from_token_contract.functions.balanceOf(self.client.account.address).call(),
                from_token_contract.functions.decimals().call()
            )
            token_amount = TokenAmount(
                amount=from_token_balance,
                decimals=from_token_decimals,
                wei=True
            )

        from_token_price_dollar = await self.client.get_token_price(token_symbol=from_token_symbol)
        to_token_price_dollar = await self.client.get_token_price('ETH')

        amount_out_min = TokenAmount(
            amount=(float(token_amount.Ether)
                * from_token_price_dollar
                / to_token_price_dollar
                * (100 - slippage) / 100),
            decimals=to_token_decimals
        )
        
        await self._approve_token_if_needed(
            token_contract=from_token_contract,
            router_address=router_contract.address,
            token_amount=token_amount
        )
            
        b_path = b''
        for address in path:
            address = AsyncWeb3.to_checksum_address(address)
            b_path += AsyncWeb3.to_bytes(hexstr=address)

        first_data = router_contract.encodeABI(
            'exactInput',
            args=[(
                b_path,
                Tokens.ZERO,
                int(time.time()) + 3 * 60,
                token_amount.Wei,
                amount_out_min.Wei,
            )]
        )
        second_data = router_contract.encodeABI(
            'unwrapWETH9',
            args=(amount_out_min.Wei, self.client.account.address)
        )
        tx_hash_bytes = await self.client.send_transaction(
            to=router_contract.address,
            data=router_contract.encodeABI(
                'multicall',
                args=[[first_data, second_data]]
            ),
            value=token_amount.Wei,
            max_priority_fee_per_gas=0,
        )

        # Why not using args=[first_data, second_data] ?
        # Because of the function signature: multicall(bytes[])
        # If we have function signature: function_name(arg_1, arg_2, ...), then we use args=[arg_1, arg_2, ...]
        # but when function signature is function_name(bytes[], ...), then we use args=[[arg_1, arg_2], ...]

        if tx_hash_bytes:
            try:
                tx_hash = await self.client.verif_tx(tx_hash=tx_hash_bytes)
                print(f'Transaction success ({token_amount.Ether} {from_token_symbol} -> {amount_out_min.Ether} ETH)!! '
                      f'tx_hash: {tx_hash}')
            except Exception as err:
                print(f'Transaction error!! tx_hash: {tx_hash_bytes.hex()}; error: {err}')
        else:
            print(f'Transaction error!!')
        
    async def swap_usdc_to_mav(
        self,
        token_amount: TokenAmount | None = None,
        slippage: float = 1,
        is_all_balance: bool = False
    ):
        """
        Function signature: 0xc04b8d59 - exactInput((bytes,address,uint256,uint256,uint256))
        000: 0000000000000000000000000000000000000000000000000000000000000020 - ссылка на 20 байт
        020: 00000000000000000000000000000000000000000000000000000000000000a0 - размер структуры (160 байт), 
                                                                                160 / 32 = 5 - cлед 5 строк - это структура (tuple)
        040: 0000000000000000000000002f5844b8b5c03bbc48408bfda1340f5181643f53 - address
        060: 000000000000000000000000000000000000000000000000000000006734c77a - deadline (int(time.time() + 10 * 60))
        080: 00000000000000000000000000000000000000000000000000000000004b8e30 - amountIn (4_951_600 USDC)
        0a0: 000000000000000000000000000000000000000000000001875e8c616665fa1f - amountOutMin (28_201_132_266_598_300_191 MAV)
        0c0: 0000000000000000000000000000000000000000000000000000000000000064 - размер массива байтов (100 байт), 
                                                                                100 / 5 = 20 bytes = 40 hexs
        0e0: 1d17cbcf0d6d143135ae902365d2e5e2a16538d4ef1cada686c12f7a0008cd5b - 1d17cbcf0d6d143135ae902365d2e5e2a16538d4 USDC
        100: 78eefaad35ad6f013355df6d4c9c3035724fd0e3914de96a5a83aaf474e398c7 - ef1cada686c12f7a0008cd5b78eefaad35ad6f01 pool USDC/USDC.e  
        120: 9eb7a653b432f6313edf776c8d930142787c09494ec8bcb24dcaf8659e7d5d69 - 3355df6d4c9c3035724fd0e3914de96a5a83aaf4 USDC.e
        140: 979ee50800000000000000000000000000000000000000000000000000000000 - 74e398c79eb7a653b432f6313edf776c8d930142 USDC.e/MAV
                                                                                787c09494ec8bcb24dcaf8659e7d5d69979ee508 MAV
        """
        path = [
            Tokens.USDC,
            'ef1cada686c12f7a0008cd5b78eefaad35ad6f01',  # pool USDC/USDC.e  
            Tokens.USDC_E,
            '74e398c79eb7a653b432f6313edf776c8d930142',  # pool USDC.e/MAV
            Tokens.STAR,
        ]

        from_token_contract = self.client.w3.eth.contract(
            address=AsyncWeb3.to_checksum_address(path[0]),
            abi=ABIs.TokenABI
        )
        to_token_contract = self.client.w3.eth.contract(
            address=AsyncWeb3.to_checksum_address(path[-1]),
            abi=ABIs.TokenABI
        )
        router_contract = self.client.w3.eth.contract(
            address=AsyncWeb3.to_checksum_address('0x39E098A153Ad69834a9Dac32f0FCa92066aD03f4'),
            abi=ABIs.MaverickABI
        )

        from_token_symbol, to_token_decimals = await asyncio.gather(
            from_token_contract.functions.symbol().call(),
            to_token_contract.functions.decimals().call(),
        )

        if is_all_balance:
            from_token_balance, from_token_decimals = await asyncio.gather(
                from_token_contract.functions.balanceOf(self.client.account.address).call(),
                from_token_contract.functions.decimals().call()
            )
            token_amount = TokenAmount(
                amount=from_token_balance,
                decimals=from_token_decimals,
                wei=True
            )

        from_token_price_dollar = await self.client.get_token_price(from_token_symbol)
        to_token_price_dollar = await self.client.get_token_price('MAV')

        amount_out_min = TokenAmount(
            amount=(float(token_amount.Ether)
                * from_token_price_dollar
                / to_token_price_dollar
                * (100 - slippage) / 100),
            decimals=to_token_decimals
        )

        await self._approve_token_if_needed(
            token_contract=from_token_contract,
            router_address=router_contract.address,
            token_amount=token_amount
        )

        b_path = b''
        for address in path:
            address = AsyncWeb3.to_checksum_address(address)
            b_path += AsyncWeb3.to_bytes(hexstr=address)

        first_data = router_contract.encodeABI(
            'exactInput',
            args=[(
                b_path,
                self.client.account.address,
                int(time.time()) + 10 * 60,
                token_amount.Wei,
                amount_out_min.Wei,
            )]
        )
        tx_hash_bytes = await self.client.send_transaction(
            to=router_contract.address,
            data=router_contract.encodeABI(
                'multicall',
                args=[[first_data]]
            ),
            value=token_amount.Wei,
            max_priority_fee_per_gas=0,
        )

        if tx_hash_bytes:
            try:
                tx_hash = await self.client.verif_tx(tx_hash=tx_hash_bytes)
                print(f'Transaction success ({token_amount.Ether} {from_token_symbol} -> {amount_out_min.Ether} MAV)!! '
                      f'tx_hash: {tx_hash}')
            except Exception as err:
                print(f'Transaction error!! tx_hash: {tx_hash_bytes.hex()}; error: {err}')
        else:
            print(f'Transaction error!!')
