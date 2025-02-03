import asyncio
import random
import time

from web3 import AsyncWeb3

from client import Client
from data.config import KOI_FINANCE_ROUTER_ABI
from data.models import ABIs, TokenAmount
from utils.files_utils import read_json
from tasks.base import Base

class KoiFinance(Base):
    def __init__(self, client: Client):
        super().__init__(client)
        self.router_abi = read_json(KOI_FINANCE_ROUTER_ABI)

    async def swap_eth_to_usdc(
        self,
        token_amount: TokenAmount,
        slippage: float = 1
    ):
        weth_address = AsyncWeb3.to_checksum_address('0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91')
        usdc_address = AsyncWeb3.to_checksum_address('0x1d17CBcF0D6D143135aE902365D2E5e2A16538D4')
        usdc_e_address = AsyncWeb3.to_checksum_address('0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4')
        
        to_token_contract = self.client.w3.eth.contract(
            address=usdc_address,
            abi=ABIs.TokenABI
        )

        # адрес свапалки
        router_address = AsyncWeb3.to_checksum_address('0x3388530FbaF0C916fA7C0390413DFB178Cb33CBb')
        router_contract = self.client.w3.eth.contract(
            address=router_address,
            abi=self.router_abi
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
             + self.to_cut_hex_prefix_and_zfill(weth_address)
             + self.to_cut_hex_prefix_and_zfill(usdc_e_address)
             + self.to_cut_hex_prefix_and_zfill(1)
             + self.to_cut_hex_prefix_and_zfill(usdc_e_address)
             + self.to_cut_hex_prefix_and_zfill(usdc_address)
             + self.to_cut_hex_prefix_and_zfill("")),

            ('0x'
             + self.to_cut_hex_prefix_and_zfill(1)
             + self.to_cut_hex_prefix_and_zfill(hex(big_amount_in_wei))
             + self.to_cut_hex_prefix_and_zfill(hex(big_amount_out_wei))
             + self.to_cut_hex_prefix_and_zfill("a0")
             + self.to_cut_hex_prefix_and_zfill("")
             + self.to_cut_hex_prefix_and_zfill(2)
             + self.to_cut_hex_prefix_and_zfill(weth_address)
             + self.to_cut_hex_prefix_and_zfill(usdc_e_address)
             + self.to_cut_hex_prefix_and_zfill(1)
             + self.to_cut_hex_prefix_and_zfill(usdc_e_address)
             + self.to_cut_hex_prefix_and_zfill(usdc_address)
             + self.to_cut_hex_prefix_and_zfill(""))
        ]

        tx_hash_bytes = await self.client.send_transaction(
            to=router_address,
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

        if tx_hash_bytes:
            try:
                tx_hash = await self.client.verif_tx(tx_hash=tx_hash_bytes)
                print(f'Transaction success ({token_amount.Ether} ETH -> {amount_out_min.Ether} USDC)!! '
                      f'tx_hash: {tx_hash}')
            except Exception as err:
                print(f'Transaction error!! tx_hash: {tx_hash_bytes.hex()}; error: {err}')
        else:
            print(f'Transaction error!!')
    