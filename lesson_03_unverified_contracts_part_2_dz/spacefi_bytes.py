import asyncio
import time

from web3 import AsyncWeb3

import config
from client import Client
from data.models import ABIs, TokenAmount


'''
0x7ff36ab5
000 000000000000000000000000000000000000000000000000000000000021626d  # 2187885 (amount out min)
020 0000000000000000000000000000000000000000000000000000000000000080  # cсылка на байт 80 (16 СС)
040 00000000000000000000000036f302d18dcede1ab1174f47726e62212d1ccead  # address
060 0000000000000000000000000000000000000000000000000000000066e84acc  # 1726499532 deadline
080 0000000000000000000000000000000000000000000000000000000000000004  # длина массива
0A0 0000000000000000000000005aea5775959fbc2557cc8789bc1bf90a239d9a91  # WETH
0C0 000000000000000000000000838a66f841dd5148475a8918db0732c239499a03  # STAR
0E0 0000000000000000000000003355df6d4c9c3035724fd0e3914de96a5a83aaf4  # USDC.e
100 0000000000000000000000001d17cbcf0d6d143135ae902365d2e5e2a16538d4  # USDC

0xc671639d
0000000000000000000000000000000000000000000000000000000000005cc0
0000000000000000000000000000000000000000000000000000000000000080
00000000000000000000000036f302d18dcede1ab1174f47726e62212d1ccead
0000000000000000000000000000000000000000000000000000000067193976
0000000000000000000000000000000000000000000000000000000000000004
0000000000000000000000005aea5775959fbc2557cc8789bc1bf90a239d9a91
000000000000000000000000838a66f841dd5148475a8918db0732c239499a03
0000000000000000000000003355df6d4c9c3035724fd0e3914de96a5a83aaf4
0000000000000000000000001d17cbcf0d6d143135ae902365d2e5e2a16538d4
'''


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
        abi=ABIs.SpaceFiABIBytes
    )

    from_token_price_dollar = await client.get_token_price(token_symbol=from_token_symbol)
    to_token_price_dollar = await client.get_token_price(token_symbol=to_token_symbol)
    amount_out_min = TokenAmount(
        amount=float(from_token_amount.Ether) * from_token_price_dollar / to_token_price_dollar * (
                    100 - slippage) / 100,
        decimals=await to_token_contract.functions.decimals().call()
    )

    data = router_contract.encodeABI('swap',
                                     args=(
                                         amount_out_min.Wei,
                                         path,
                                         client.account.address,
                                         int(time.time() + 1200)
                                     ))
    data = '0x7ff36ab5' + data[10:]

    tx_hash = await client.send_transaction(
        to=router_address,
        data=data,
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
