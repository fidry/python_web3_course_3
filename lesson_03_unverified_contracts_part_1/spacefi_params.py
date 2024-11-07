import asyncio
import time

from web3 import AsyncWeb3

import config
from client import Client
from data.models import ABIs, TokenAmount


async def main(from_token_amount: TokenAmount, slippage: float = 5):
    client = Client(
        private_key=config.PRIVATE_KEY,
        rpc='https://mainnet.era.zksync.io',
        proxy=config.PROXY
    )

    path = [
        AsyncWeb3.to_checksum_address('0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91'),  # WETH
        AsyncWeb3.to_checksum_address('0x838A66F841DD5148475a8918db0732c239499a03'),  # STAR
        AsyncWeb3.to_checksum_address('0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4'),  # USDC.e
        AsyncWeb3.to_checksum_address('0x1d17CBcF0D6D143135aE902365D2E5e2A16538D4'),  # USDC
    ]

    from_token_address = path[0]
    from_token_contract = client.w3.eth.contract(
        address=from_token_address,
        abi=ABIs.TokenABI
    )
    from_token_symbol = await from_token_contract.functions.symbol().call()

    to_token_address = path[-1]
    to_token_contract = client.w3.eth.contract(
        address=to_token_address,
        abi=ABIs.TokenABI
    )
    to_token_symbol = await to_token_contract.functions.symbol().call()

    # адрес свапалки
    router_address = AsyncWeb3.to_checksum_address('0xbE7D1FD1f6748bbDefC4fbaCafBb11C6Fc506d1d')
    router_contract = client.w3.eth.contract(
        address=router_address,
        abi=ABIs.SpaceFiABI
    )

    from_token_price_dollar = await client.get_token_price(token_symbol=from_token_symbol)
    to_token_price_dollar = await client.get_token_price(token_symbol=to_token_symbol)
    amount_out_min = TokenAmount(
        amount=float(from_token_amount.Ether) * from_token_price_dollar / to_token_price_dollar * (
                    100 - slippage) / 100,
        decimals=await to_token_contract.functions.decimals().call()
    )

    tx_hash = await client.send_transaction(
        to=router_address,
        data=router_contract.encodeABI('swapExactETHForTokens',
                                       args=(
                                           amount_out_min.Wei,
                                           path,
                                           client.account.address,
                                           int(time.time() + 1200)
                                       )),
        value=from_token_amount.Wei,
        max_priority_fee_per_gas=0
    )

    if tx_hash:
        try:
            await client.verif_tx(tx_hash=tx_hash)
            print(f'Transaction success ({from_token_amount.Ether} ETH -> {amount_out_min.Ether} {to_token_symbol})!! '
                  f'tx_hash: {tx_hash.hex()}')
            # Transaction success (0.001 ETH -> 2.28988 USDC)!! tx_hash: 0x5e97aaaa972dc2aca2bdb8b6241fe6dd5bb9eaeb238d0dcd941c31c46198b51e
        except Exception as err:
            print(f'Transaction error!! tx_hash: {tx_hash.hex()}; error: {err}')
    else:
        print(f'Transaction error!!')


if __name__ == '__main__':
    amount = TokenAmount(0.00001)
    asyncio.run(main(from_token_amount=amount))
