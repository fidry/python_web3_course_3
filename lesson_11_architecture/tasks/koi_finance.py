import time
import random
import asyncio

from tasks.base import Base
from data.models import TokenAmount, Contracts


class KoiFinance(Base):
    async def _swap_eth_to_usdc(
        self,
        token_amount: TokenAmount | None = None,
        slippage: float = 1
    ) -> str:
        to_token = Contracts.USDC
        router = Contracts.KOI_FINANCE_ROUTER

        if not token_amount:
            token_amount = self.get_eth_amount_for_swap()

        failed_text = f'Failed to swap ETH to {to_token.title} via {router.title}'

        to_token_contract = self.client.w3.eth.contract(
            address=to_token.address,
            abi=to_token.abi
        )

        router_contract = self.client.w3.eth.contract(
            address=router.address,
            abi=router.abi
        )

        from_token_price_dollar, to_token_price_dollar = await asyncio.gather(
            self.client.get_token_price(token_symbol='ETH'),
            self.client.get_token_price(token_symbol='USDC')
        )

        swap_ratios = [0.2, 0.4]
        selected_small_ratio = random.choice(swap_ratios)
        # selected_small_ratio = random.uniform(0.2, 0.4)
        selected_big_ratio = 1 - selected_small_ratio

        amount_out_min = TokenAmount(
            amount=(
                float(token_amount.Ether)
                * from_token_price_dollar
                / to_token_price_dollar
                * (100 - slippage) / 100
            ),
            decimals=to_token_contract.functions.decimals().call()
        )
        small_amount_in_wei = int(token_amount.Wei * selected_small_ratio)
        big_amount_in_wei = int(token_amount.Wei * selected_big_ratio)

        small_amount_out_wei = int(amount_out_min.Wei * selected_small_ratio)
        big_amount_out_wei = int(amount_out_min.Wei * selected_big_ratio)

        inputs = [
            ('0x'
             + self.to_cut_hex_prefix_and_zfill(2)
             + self.to_cut_hex_prefix_and_zfill(hex(token_amount.Wei))),
            
            ('0x'
             + self.to_cut_hex_prefix_and_zfill(1)
             + self.to_cut_hex_prefix_and_zfill(hex(small_amount_in_wei))
             + self.to_cut_hex_prefix_and_zfill(hex(small_amount_out_wei))
             + self.to_cut_hex_prefix_and_zfill("a0")
             + self.to_cut_hex_prefix_and_zfill("")
             + self.to_cut_hex_prefix_and_zfill(2)
             + self.to_cut_hex_prefix_and_zfill(Contracts.WETH.address)
             + self.to_cut_hex_prefix_and_zfill(Contracts.USDC_E.address)
             + self.to_cut_hex_prefix_and_zfill(1)
             + self.to_cut_hex_prefix_and_zfill(Contracts.USDC_E.address)
             + self.to_cut_hex_prefix_and_zfill(Contracts.USDC.address)
             + self.to_cut_hex_prefix_and_zfill("")),

            ('0x'
             + self.to_cut_hex_prefix_and_zfill(1)
             + self.to_cut_hex_prefix_and_zfill(hex(big_amount_in_wei))
             + self.to_cut_hex_prefix_and_zfill(hex(big_amount_out_wei))
             + self.to_cut_hex_prefix_and_zfill("a0")
             + self.to_cut_hex_prefix_and_zfill("")
             + self.to_cut_hex_prefix_and_zfill(2)
             + self.to_cut_hex_prefix_and_zfill(Contracts.WETH.address)
             + self.to_cut_hex_prefix_and_zfill(Contracts.USDC_E.address)
             + self.to_cut_hex_prefix_and_zfill(1)
             + self.to_cut_hex_prefix_and_zfill(Contracts.USDC_E.address)
             + self.to_cut_hex_prefix_and_zfill(Contracts.USDC.address)
             + self.to_cut_hex_prefix_and_zfill(""))
        ]

        tx_hash_bytes = await self.client.send_transaction(
            to=router.address,
            data=router_contract.encodeABI(
                'execute',
                args=(
                    '0x0b0808',
                    inputs,
                    int(time.time() + 1200)
                )),
            value=token_amount.Wei,
            max_priority_fee_per_gas=0,
        )

        if not tx_hash_bytes:
            return f'{failed_text} | Can not get tx_hash_bytes'

        try:
            tx_hash = await self.client.verif_tx(tx_hash=tx_hash_bytes)
            return (f'Transaction success! ({token_amount.Ether} ETH -> {amount_out_min.Ether} {to_token.title}) | '
                    f'tx_hash: {tx_hash}')
        except Exception as err:
            return f' {failed_text} | tx_hash: {tx_hash_bytes.hex()}; error: {err}'
