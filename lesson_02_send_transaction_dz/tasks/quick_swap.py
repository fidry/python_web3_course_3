import asyncio
import time
from eth_typing import Address
from hexbytes import HexBytes

from web3 import AsyncWeb3
from web3.contract.async_contract import AsyncContract

from client import Client
from data.models import TokenABI
from utils import get_json


def get_address_in_polygon(token_name: str) -> str:
    token_dict: dict[str, Address] = {
        'USDC': '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359',
        'USDT': '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
        'WETH': '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',
        'WMATIC': '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270',
        'QUICK': '0x831753DD7087CaC61aB5644b308642cc1c33Dc13',
        'miMATIC': '0xa3Fa99A148fA48D14Ed51d610c367C61876997F1'
    }

    if token_name not in token_dict:
        raise Exception(f'Token {token_name} not supported for swap')

    return AsyncWeb3.to_checksum_address(token_dict[token_name])


def get_decimals_in_polygon(token_name: str) -> int:
    decimals_dict: dict[str, int] = {
        'WMATIC': 18,
        'POL': 18,
        'WETH': 18,
        'USDC': 6,
        'USDT': 6
    }

    if token_name.upper() not in decimals_dict:
        raise Exception(f'{token_name} token decimals unknown')

    return decimals_dict[token_name.upper()]


class QuickSwap:
    def __init__(self, client: Client):
        self.client = client
        self.router_address: str = AsyncWeb3.to_checksum_address(
            '0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff'
        )
        self.router_abi_path = ('data', 'abis', 'quickswap', 'router_abi.json')

    async def get_raw_tx_params(self, value: float = 0) -> dict:
        return {
            "chainId": await self.client.w3.eth.chain_id,
            "from": self.client.account.address,
            "value": value,
            "gasPrice": await self.client.w3.eth.gas_price,
            "nonce": await self.client.w3.eth.get_transaction_count(self.client.account.address),
        }

    async def swap_native_to_token(
        self,
        native_amount: int | float,
        token_name: str,
        slippage: float = 0.5
    ) -> HexBytes | None:
        to_token_address = get_address_in_polygon(token_name)
        token_decimals = get_decimals_in_polygon(token_name)
        native_decimals = get_decimals_in_polygon('POL')

        if not to_token_address or not token_decimals:
            return 'Failed'

        contract: AsyncContract = self.client.w3.eth.contract(
            address=self.router_address, abi=get_json(self.router_abi_path)
        )

        value = int(native_amount * 10 ** native_decimals)
        amount_out_min = int(
            native_amount
            * await self.client.get_token_price('POL')
            * (1 - slippage / 100)
            * 10 ** token_decimals
        )
        
        tx_params = await contract.functions.swapExactETHForTokens(
            amount_out_min,
            [
                get_address_in_polygon('WMATIC'),
                get_address_in_polygon('WETH'),
                to_token_address,
            ],
            self.client.account.address,
            2 * int(time.time() + 20 * 60)
        ).build_transaction(await self.get_raw_tx_params(value))
        
        signed_tx = self.client.w3.eth.account.sign_transaction(tx_params, self.client.private_key)
        tx_hash_bytes = await self.client.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = await self.client.w3.eth.wait_for_transaction_receipt(tx_hash_bytes)
        
        return tx_hash_bytes.hex() if receipt['status'] else 'Failed'

    async def swap_token_to_native(
        self,
        token_name: str,
        amount: int | float,
        slippage: float = 0.5
    ) -> HexBytes | None:
        token_address = get_address_in_polygon(token_name.upper())
        token_decimals = get_decimals_in_polygon(token_name)
        native_decimals = get_decimals_in_polygon('POL')
        
        if not token_address or not token_decimals:
            return 'Failed'

        contract: AsyncContract = self.client.w3.eth.contract(
            address=self.router_address, abi=get_json(self.router_abi_path)
        )
        token_contract: AsyncContract = self.client.w3.eth.contract(
            address=token_address, abi=TokenABI
        )
        
        amount_in = int(amount * 10 ** token_decimals)
        amount_out_min = int(
            amount
            * await self.client.get_token_price(token_name.upper())
            * (1 - slippage / 100)
            * 10 ** native_decimals
        )
        
        tx_params = await token_contract.functions.approve(
            self.router_address,
            amount_in
        ).build_transaction(await self.get_raw_tx_params())
        
        signed_tx = self.client.w3.eth.account.sign_transaction(tx_params, self.client.private_key)
        tx_hash_bytes = await self.client.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = await self.client.w3.eth.wait_for_transaction_receipt(tx_hash_bytes)
        
        if receipt['status']:
            waiting_time = 15
            print(
                f'Approved {amount} {token_name} to swap on QuickSwap, '
                f'sleeping {waiting_time} secs...'
            )
            await asyncio.sleep(waiting_time)
        else:
            return 'Failed'
        
        data = contract.encodeABI(
            fn_name='swapExactTokensForETH',
            args=(
                amount_in,
                amount_out_min,
                [
                    token_address,
                    get_address_in_polygon('WETH'),
                    get_address_in_polygon('WMATIC'),
                ],
                self.client.account.address,
                2 * int(time.time() + 20 * 60)
            )
        )

        tx_hash_bytes = await self.client.send_transaction(
            to=self.router_address,
            data=data,
        )
        receipt = await self.client.w3.eth.wait_for_transaction_receipt(tx_hash_bytes)
        
        return tx_hash_bytes.hex() if receipt['status'] else 'Failed'