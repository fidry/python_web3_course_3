import asyncio
import random
import time

from web3 import AsyncWeb3
from uniswap_universal_router_decoder import RouterCodec, FunctionRecipient

from client import Client
from data.models import ABIs, Permit2ABI, TokenAmount, Tokens
from utils import TxUtils


class KoiFinance:
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

    async def swap_eth_to_usdc(
        self,
        token_amount: TokenAmount,
        slippage: float = 1
    ):
        from_token_address = Tokens.WETH
        from_token_contract = self.client.w3.eth.contract(
            address=from_token_address,
            abi=ABIs.TokenABI
        )
        to_token_address = Tokens.USDC
        to_token_contract = self.client.w3.eth.contract(
            address=to_token_address,
            abi=ABIs.TokenABI
        )
        from_token_symbol, to_token_symbol, to_token_decimals = await asyncio.gather(
            from_token_contract.functions.symbol().call(),
            to_token_contract.functions.symbol().call(),
            to_token_contract.functions.decimals().call()
        )

        # адрес свапалки
        router_address = AsyncWeb3.to_checksum_address('0x3388530FbaF0C916fA7C0390413DFB178Cb33CBb')
        router_contract = self.client.w3.eth.contract(
            address=router_address,
            abi=ABIs.KoiFinance
        )

        from_token_price_dollar, to_token_price_dollar = await asyncio.gather(
            self.client.get_token_price(token_symbol=from_token_symbol),
            self.client.get_token_price(token_symbol=to_token_symbol)
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
            decimals=to_token_decimals
        )
        small_amount_in_wei = int(token_amount.Wei * selected_small_ratio)
        big_amount_in_wei = int(token_amount.Wei * selected_big_ratio)

        small_amount_out_wei = int(amount_out_min.Wei * selected_small_ratio)
        big_amount_out_wei = int(amount_out_min.Wei * selected_big_ratio)

        inputs = [
            ('0x'
             + TxUtils.to_cut_hex_prefix_and_zfill(2)
             + TxUtils.to_cut_hex_prefix_and_zfill(hex(token_amount.Wei))),
            
            ('0x'
             + TxUtils.to_cut_hex_prefix_and_zfill(1)
             + TxUtils.to_cut_hex_prefix_and_zfill(hex(small_amount_in_wei))
             + TxUtils.to_cut_hex_prefix_and_zfill(hex(small_amount_out_wei))
             + TxUtils.to_cut_hex_prefix_and_zfill("a0")
             + TxUtils.to_cut_hex_prefix_and_zfill("")
             + TxUtils.to_cut_hex_prefix_and_zfill(2)
             + TxUtils.to_cut_hex_prefix_and_zfill(Tokens.WETH)
             + TxUtils.to_cut_hex_prefix_and_zfill(Tokens.USDC_E)
             + TxUtils.to_cut_hex_prefix_and_zfill(1)
             + TxUtils.to_cut_hex_prefix_and_zfill(Tokens.USDC_E)
             + TxUtils.to_cut_hex_prefix_and_zfill(Tokens.USDC)
             + TxUtils.to_cut_hex_prefix_and_zfill("")),

            ('0x'
             + TxUtils.to_cut_hex_prefix_and_zfill(1)
             + TxUtils.to_cut_hex_prefix_and_zfill(hex(big_amount_in_wei))
             + TxUtils.to_cut_hex_prefix_and_zfill(hex(big_amount_out_wei))
             + TxUtils.to_cut_hex_prefix_and_zfill("a0")
             + TxUtils.to_cut_hex_prefix_and_zfill("")
             + TxUtils.to_cut_hex_prefix_and_zfill(2)
             + TxUtils.to_cut_hex_prefix_and_zfill(Tokens.WETH)
             + TxUtils.to_cut_hex_prefix_and_zfill(Tokens.USDC_E)
             + TxUtils.to_cut_hex_prefix_and_zfill(1)
             + TxUtils.to_cut_hex_prefix_and_zfill(Tokens.USDC_E)
             + TxUtils.to_cut_hex_prefix_and_zfill(Tokens.USDC)
             + TxUtils.to_cut_hex_prefix_and_zfill(""))
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
                print(f'Transaction success ({token_amount.Ether} ETH -> {amount_out_min.Ether} {to_token_symbol})!! '
                      f'tx_hash: {tx_hash}')
                # Transaction success (0.001 ETH -> 2.28988 USDC)!! tx_hash: 0x5e97aaaa972dc2aca2bdb8b6241fe6dd5bb9eaeb238d0dcd941c31c46198b51e
            except Exception as err:
                print(
                    f'Transaction error!! tx_hash: {tx_hash_bytes.hex()}; error: {err}')
        else:
            print(f'Transaction error!!')
