'''
5aea5775959fbc2557cc8789bc1bf90a239d9a91 WETH
66aed71a8d53b5f4f02764284d4b0745e7ef288a -
3355df6d4c9c3035724fd0e3914de96a5a83aaf4 USDC_E
ef1cada686c12f7a0008cd5b78eefaad35ad6f01 -
1d17cbcf0d6d143135ae902365d2e5e2a16538d4 USDC
'''

import asyncio
import time

from web3 import AsyncWeb3

import config
from client import Client
from data.models import ABIs, TokenAmount, Tokens


async def main(from_token_amount: TokenAmount, slippage: float = 5):
    client = Client(
        private_key=config.PRIVATE_KEY,
        rpc='https://mainnet.era.zksync.io',
        proxy=config.PROXY
    )

    path = [
        Tokens.WETH,
        AsyncWeb3.to_checksum_address('66aed71a8d53b5f4f02764284d4b0745e7ef288a'),  # pool1
        Tokens.USDC_E,  # USDC.e
        AsyncWeb3.to_checksum_address('ef1cada686c12f7a0008cd5b78eefaad35ad6f01'),  # pool2
        Tokens.USDC,  # USDC
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
    router_address = AsyncWeb3.to_checksum_address('0x39E098A153Ad69834a9Dac32f0FCa92066aD03f4')
    router_contract = client.w3.eth.contract(
        address=router_address,
        abi=ABIs.MavericABI
    )

    from_token_price_dollar = await client.get_token_price(token_symbol=from_token_symbol)
    to_token_price_dollar = await client.get_token_price(token_symbol=to_token_symbol)
    amount_out_min = TokenAmount(
        amount=float(from_token_amount.Ether) * from_token_price_dollar / to_token_price_dollar * (
                100 - slippage) / 100,
        decimals=await to_token_contract.functions.decimals().call()
    )

    b_path = []
    for address in path:
        b_path.append(
            # переводим адрес из строки в байты и добавляем в список
            AsyncWeb3.to_bytes(hexstr=address)
        )
    joined_path = b''.join(b_path)

    args = (
        joined_path,
        client.account.address,
        int(time.time()) + 1200,
        from_token_amount.Wei,
        amount_out_min.Wei,
    )

    data = router_contract.encodeABI('exactInput', args=[args])
    second_item = router_contract.encodeABI('refundETH', args=[])

    tx_hash = await client.send_transaction(
        to=router_address,
        data=router_contract.encodeABI('multicall', args=[
            [data, second_item]
        ]),
        value=from_token_amount.Wei,
        max_priority_fee_per_gas=client.max_priority_fee()
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
