import asyncio
import time
from web3 import AsyncWeb3
from client import Client
from data.models import ABIs, TokenAmount


class SpaceFi:
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

    async def swap_eth_to_usdt(
        self, 
        token_amount: TokenAmount, 
        slippage: float = 0.5
    ):
        path = [
            AsyncWeb3.to_checksum_address('0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91'), # WETH
            AsyncWeb3.to_checksum_address('0x493257fD37EDB34451f62EDf8D2a0C418852bA4C')  # USDT
        ]

        from_token_address = path[0]
        from_token_contract = self.client.w3.eth.contract(
            address=from_token_address,
            abi=ABIs.TokenABI
        )
        to_token_address = path[-1]
        to_token_contract = self.client.w3.eth.contract(
            address=to_token_address,
            abi=ABIs.TokenABI
        )
        from_token_symbol, to_token_symbol = await asyncio.gather(
            from_token_contract.functions.symbol().call(),
            to_token_contract.functions.symbol().call(),
        )

        router_address = AsyncWeb3.to_checksum_address('0xbE7D1FD1f6748bbDefC4fbaCafBb11C6Fc506d1d')
        router_contract = self.client.w3.eth.contract(
            address=router_address,
            abi=ABIs.SpaceFiABI
        )
        from_token_price_dollar, to_token_price_dollar = await asyncio.gather(
            self.client.get_token_price(token_symbol=from_token_symbol),
            self.client.get_token_price(token_symbol=to_token_symbol)
        )

        amount_out_min = TokenAmount(
            amount=float(token_amount.Ether) 
                * from_token_price_dollar 
                / to_token_price_dollar 
                * (100 - slippage) / 100,
            decimals=await to_token_contract.functions.decimals().call()
        )

        tx_params = await router_contract.functions.swapExactETHForTokens(
            amount_out_min.Wei,
            path,
            self.client.account.address,
            int(time.time() + 1200)
        ).build_transaction(
            await self.get_raw_tx_params(wei_value=token_amount.Wei)
        )

        signed_tx = self.client.w3.eth.account.sign_transaction(
            tx_params, 
            self.client.private_key
        )
        tx_hash_bytes = await self.client.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = await self.client.w3.eth.wait_for_transaction_receipt(tx_hash_bytes)
        
        if receipt['status']:
            try:
                await self.client.verif_tx(tx_hash=tx_hash_bytes)
                print(f'Transaction success ({token_amount.Ether} {from_token_symbol} -> {amount_out_min.Ether} {to_token_symbol})!! '
                    f'tx_hash: {tx_hash_bytes.hex()}')
                # Transaction success (0.001 ETH -> 2.87 USDT)!! tx_hash: 0x358ab333050193e02623c0b81aad6acea73f358eabd35e6c7526a5e7f52b98db
            except Exception as err:
                print(f'Transaction error!! tx_hash: {tx_hash_bytes.hex()}; error: {err}')
        else:
            print(f'Transaction error!!')

    async def swap_eth_to_wbtc(
        self,
        token_amount: TokenAmount,
        slippage: float = 0.5
    ):
        path = {
            'ETH': AsyncWeb3.to_checksum_address('0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91'),  # WETH
            'WBTC': AsyncWeb3.to_checksum_address('0xBBeB516fb02a01611cBBE0453Fe3c580D7281011')  # WBTC
        }

        to_token_address = path['WBTC']
        to_token_contract = self.client.w3.eth.contract(
            address=to_token_address,
            abi=ABIs.TokenABI
        )

        router_address = AsyncWeb3.to_checksum_address('0xbE7D1FD1f6748bbDefC4fbaCafBb11C6Fc506d1d')
        router_contract = self.client.w3.eth.contract(
            address=router_address,
            abi=ABIs.SpaceFiABI
        )

        from_token_price_dollar = await self.client.get_token_price(token_symbol='ETH')
        to_token_price_dollar = await self.client.get_token_price(token_symbol='WBTC')

        amount_out_min = TokenAmount(
            amount=float(token_amount.Ether) 
                * from_token_price_dollar 
                / to_token_price_dollar 
                * (100 - slippage) / 100,
            decimals=await to_token_contract.functions.decimals().call()
        )

        tx_hash = await self.client.send_transaction(
            to=router_address,
            data = router_contract.encodeABI(
                'swapExactTokensForETH',
                args=(
                    token_amount.Wei,
                    amount_out_min.Wei,
                    path,
                    self.client.account.address,
                    int(time.time() + 1200)
                )
            ),
            value=token_amount.Wei,
            max_priority_fee_per_gas=0
        )

        if tx_hash:
            try:
                await self.client.verif_tx(tx_hash=tx_hash)
                print(f'Transaction success ({token_amount.Ether} ETH -> {amount_out_min.Ether} WBTC)!! '
                    f'tx_hash: {tx_hash.hex()}')
                # Transaction success (0.0008 ETH -> 0.000029105322888639857 WBTC)!! tx_hash: 0x669310c1ec16ed385e8d0778cc96c05e2bc3d8b2e6d3490f4363b370bc6d2446
            except Exception as err:
                print(f'Transaction error!! tx_hash: {tx_hash.hex()}; error: {err}')
        else:
            print(f'Transaction error!!')

    async def swap_usdc_e_to_eth(
        self, 
        token_amount: TokenAmount, 
        slippage: float = 0.5
    ):
        path = [
            AsyncWeb3.to_checksum_address('0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4'),  # USDC.e
            AsyncWeb3.to_checksum_address('0x47260090cE5e83454d5f05A0AbbB2C953835f777'),  # SPACE
            AsyncWeb3.to_checksum_address('0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91')   # WETH
        ]

        from_token_address = path[0]
        from_token_contract = self.client.w3.eth.contract(
            address=from_token_address,
            abi=ABIs.TokenABI
        )
        from_token_symbol = await from_token_contract.functions.symbol().call()

        to_token_address = path[-1]
        to_token_contract = self.client.w3.eth.contract(
            address=to_token_address,
            abi=ABIs.TokenABI
        )
        to_token_symbol = await to_token_contract.functions.symbol().call()

        router_address = AsyncWeb3.to_checksum_address('0xbE7D1FD1f6748bbDefC4fbaCafBb11C6Fc506d1d')
        router_contract = self.client.w3.eth.contract(
            address=router_address,
            abi=ABIs.SpaceFiABI
        )

        from_token_price_dollar = await self.client.get_token_price(token_symbol=from_token_symbol)
        to_token_price_dollar = await self.client.get_token_price(token_symbol=to_token_symbol)

        amount_out_min = TokenAmount(
            amount=float(token_amount.Ether) 
                * from_token_price_dollar 
                / to_token_price_dollar 
                * (100 - slippage) / 100,
            decimals=await to_token_contract.functions.decimals().call()
        )

        tx_hash_bytes = await self.client.send_transaction(
            to=from_token_address,
            data = from_token_contract.encodeABI(
                'approve',
                args=(
                    router_address,
                    token_amount.Wei
                )
            ),
            max_priority_fee_per_gas=0
        )

        tx_hash = await self.client.verif_tx(tx_hash_bytes)
        
        if tx_hash:
            waiting_time = 15
            print(
                f'Approved {token_amount.Ether} {from_token_symbol} to swap on SpaceFi, '
                f'sleeping {waiting_time} secs...'
            )
            await asyncio.sleep(waiting_time)
        else:
            print('Failed')

        tx_hash_bytes = await self.client.send_transaction(
            to=router_address,
            data = router_contract.encodeABI(
                'swapExactTokensForETH',
                args=(
                    token_amount.Wei,
                    amount_out_min.Wei,
                    path,
                    self.client.account.address,
                    int(time.time() + 1200)
                )
            ),
            max_priority_fee_per_gas=0
        )

        if tx_hash_bytes:
            try:
                tx_hash = await self.client.verif_tx(tx_hash=tx_hash_bytes)
                print(f'Transaction success ({token_amount.Ether} {from_token_symbol} -> {amount_out_min.Ether} {to_token_symbol})!! '
                    f'tx_hash: {tx_hash}')
                # Transaction success (1.961663 USDC.e -> 0.0006465444482972901 WETH)!! tx_hash: 0x0161e7cb528408427fce8eda171a251632d0b28cb89bf8dfd9616189964ae08b
            except Exception as err:
                print(f'Transaction error!! tx_hash: {tx_hash}; error: {err}')
        else:
            print(f'Transaction error!!')

    async def swap_usdt_to_eth(
        self, 
        token_amount: TokenAmount | None = None, 
        slippage: float = 0.5,
        is_all_balance: bool = False
    ):
        path = [
            AsyncWeb3.to_checksum_address('0x493257fD37EDB34451f62EDf8D2a0C418852bA4C'),  # USDT
            AsyncWeb3.to_checksum_address('0x47260090cE5e83454d5f05A0AbbB2C953835f777'),  # SPACE
            AsyncWeb3.to_checksum_address('0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91')   # WETH
        ]

        from_token_address = path[0]
        from_token_contract = self.client.w3.eth.contract(
            address=from_token_address,
            abi=ABIs.TokenABI
        )
        to_token_address = path[-1]
        to_token_contract = self.client.w3.eth.contract(
            address=to_token_address,
            abi=ABIs.TokenABI
        )
        from_token_symbol, to_token_symbol = await asyncio.gather(
            from_token_contract.functions.symbol().call(),
            to_token_contract.functions.symbol().call(),
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

        router_address = AsyncWeb3.to_checksum_address('0xbE7D1FD1f6748bbDefC4fbaCafBb11C6Fc506d1d')
        router_contract = self.client.w3.eth.contract(
            address=router_address,
            abi=ABIs.SpaceFiABIBytesTokenToToken
        )
        from_token_price_dollar, to_token_price_dollar = await asyncio.gather(
            self.client.get_token_price(token_symbol=from_token_symbol),
            self.client.get_token_price(token_symbol=to_token_symbol)
        )

        amount_out_min = TokenAmount(
            amount=float(token_amount.Ether) 
                * from_token_price_dollar 
                / to_token_price_dollar 
                * (100 - slippage) / 100,
            decimals=await to_token_contract.functions.decimals().call()
        )

        tx_params = await from_token_contract.functions.approve(
            router_address,
            token_amount.Wei
        ).build_transaction(await self.get_raw_tx_params())
        
        signed_tx = self.client.w3.eth.account.sign_transaction(tx_params, self.client.private_key)
        tx_hash_bytes = await self.client.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = await self.client.w3.eth.wait_for_transaction_receipt(tx_hash_bytes)
        
        if receipt['status']:
            waiting_time = 15
            print(
                f'Approved {token_amount.Ether} {from_token_symbol} to swap on SpaceFi, '
                f'sleeping {waiting_time} secs...'
            )
            await asyncio.sleep(waiting_time)
        else:
            print('Failed')
        
        data = router_contract.encodeABI(
            'swap',
            args=(
                token_amount.Wei,
                amount_out_min.Wei,
                path,
                self.client.account.address,
                int(time.time() + 1200)
            )
        )
        data = '0x18cbafe5' + data[10:]

        tx_hash_bytes = await self.client.send_transaction(
            to=router_address,
            data=data,
            max_priority_fee_per_gas=0
        )

        if tx_hash_bytes:
            try:
                tx_hash = await self.client.verif_tx(tx_hash=tx_hash_bytes)
                print(f'Transaction success ({token_amount.Ether} {from_token_symbol} -> {amount_out_min.Ether} {to_token_symbol})!! '
                    f'tx_hash: {tx_hash}')
                # Transaction success (0.0004 ETH -> 1.13988 USDT)!! tx_hash: 0x16ed6ce885e1f65a4a068b5e9253a5ebe2251ae93ed878ab583830515c627fb0
            except Exception as err:
                print(f'Transaction error!! tx_hash: {tx_hash}; error: {err}')
        else:
            print(f'Transaction error!!')
    
    async def swap_usdt_to_usdc_e(
        self,
        token_amount: TokenAmount | None = None,
        slippage: float = 0.5,
        is_all_balance: bool = False
    ):
        path = [
            AsyncWeb3.to_checksum_address('0x493257fD37EDB34451f62EDf8D2a0C418852bA4C'),  # USDT
            AsyncWeb3.to_checksum_address('0x47260090cE5e83454d5f05A0AbbB2C953835f777'),  # SPACE
            AsyncWeb3.to_checksum_address('0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4'),  # USDC.E
        ]

        from_token_address = path[0]
        from_token_contract = self.client.w3.eth.contract(
            address=from_token_address,
            abi=ABIs.TokenABI
        )
        to_token_address = path[-1]
        to_token_contract = self.client.w3.eth.contract(
            address=to_token_address,
            abi=ABIs.TokenABI
        )
        from_token_symbol, to_token_symbol = await asyncio.gather(
            from_token_contract.functions.symbol().call(),
            to_token_contract.functions.symbol().call(),
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

        router_address = AsyncWeb3.to_checksum_address('0xbE7D1FD1f6748bbDefC4fbaCafBb11C6Fc506d1d')
        router_contract = self.client.w3.eth.contract(
            address=router_address,
            abi=ABIs.SpaceFiABIBytesTokenToToken
        )

        from_token_price_dollar, to_token_price_dollar = await asyncio.gather(
            self.client.get_token_price(token_symbol=from_token_symbol),
            self.client.get_token_price(token_symbol=to_token_symbol)
        )

        amount_out_min = TokenAmount(
            amount=float(token_amount.Ether) 
                * from_token_price_dollar 
                / to_token_price_dollar 
                * (100 - slippage) / 100,
            decimals=await to_token_contract.functions.decimals().call()
        )

        tx_hash_bytes = await self.client.send_transaction(
            to=from_token_address,
            data = from_token_contract.encodeABI(
                'approve',
                args=(
                    router_address,
                    token_amount.Wei
                )
            ),
            max_priority_fee_per_gas=0
        )

        tx_hash = await self.client.verif_tx(tx_hash_bytes)
        
        if tx_hash:
            waiting_time = 15
            print(
                f'Approved {token_amount.Ether} {from_token_symbol} to swap on SpaceFi, '
                f'sleeping {waiting_time} secs...'
            )
            await asyncio.sleep(waiting_time)
        else:
            print('Failed')

        data = router_contract.encodeABI(
            'swap',
            args=(
                token_amount.Wei,
                amount_out_min.Wei,
                path,
                self.client.account.address,
                int(time.time() + 1200)
            )
        )
        data = '0x38ed1739' + data[10:]

        tx_hash_bytes = await self.client.send_transaction(
            to=router_address,
            data=data,
            max_priority_fee_per_gas=0
        )

        if tx_hash_bytes:
            try:
                tx_hash = await self.client.verif_tx(tx_hash=tx_hash_bytes)
                print(f'Transaction success ({token_amount.Ether} {from_token_symbol} -> {amount_out_min.Ether} {to_token_symbol})!! '
                    f'tx_hash: {tx_hash}')
                # Transaction success (2.027439 USDT -> 1.946341 USDC.e)!! tx_hash: 0xbd678a795c66238f067a0df7f49c759d7e3bc422a60c8fd7baadd1532566c98c
            except Exception as err:
                print(f'Transaction error!! tx_hash: {tx_hash}; error: {err}')
        else:
            print(f'Transaction error!!')