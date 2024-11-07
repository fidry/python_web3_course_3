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

    from_token_address = Tokens.WETH
    from_token_contract = client.w3.eth.contract(
        address=from_token_address,
        abi=ABIs.TokenABI
    )
    from_token_symbol = await from_token_contract.functions.symbol().call()

    to_token_address = Tokens.USDC
    to_token_contract = client.w3.eth.contract(
        address=to_token_address,
        abi=ABIs.TokenABI
    )
    to_token_symbol = await to_token_contract.functions.symbol().call()

    # адрес свапалки
    router_address = AsyncWeb3.to_checksum_address('0x3388530FbaF0C916fA7C0390413DFB178Cb33CBb')
    router_contract = client.w3.eth.contract(
        address=router_address,
        abi=ABIs.KoiFinance
    )

    from_token_price_dollar = await client.get_token_price(token_symbol=from_token_symbol)
    to_token_price_dollar = await client.get_token_price(token_symbol=to_token_symbol)
    amount_out_min = TokenAmount(
        amount=float(from_token_amount.Ether) * from_token_price_dollar / to_token_price_dollar * (
                    100 - slippage) / 100,
        decimals=await to_token_contract.functions.decimals().call()
    )

    '''
    0x
    0000000000000000000000000000000000000000000000000000000000000002 – какая-то константа
    00000000000000000000000000000000000000000000000000038d7ea4c68000 – from_token_amount
    
    0x
    0000000000000000000000000000000000000000000000000000000000000001 – какая-то константа
    00000000000000000000000000000000000000000000000000038d7ea4c68000 – from_token_amount
    0000000000000000000000000000000000000000000000000000000000224cd1 – amount_out_min
    00000000000000000000000000000000000000000000000000000000000000a0 – какая-то константа
    0000000000000000000000000000000000000000000000000000000000000000 – какая-то константа
    0000000000000000000000000000000000000000000000000000000000000003 – какая-то константа
    0000000000000000000000005aea5775959fbc2557cc8789bc1bf90a239d9a91 – WETH
    000000000000000000000000493257fd37edb34451f62edf8d2a0c418852ba4c – USDT
    0000000000000000000000000000000000000000000000000000000000000000 – какая-то константа
    000000000000000000000000493257fd37edb34451f62edf8d2a0c418852ba4c – USDT
    0000000000000000000000003355df6d4c9c3035724fd0e3914de96a5a83aaf4 – USDC.e
    0000000000000000000000000000000000000000000000000000000000000001 – какая-то константа
    0000000000000000000000003355df6d4c9c3035724fd0e3914de96a5a83aaf4 – USDC.e
    0000000000000000000000001d17cbcf0d6d143135ae902365d2e5e2a16538d4 – USDC
    0000000000000000000000000000000000000000000000000000000000000001 – какая-то константа
    '''

    inputs = [
        f'0x'                                           # 0x
        f'{"2".zfill(64)}'                              # 0000000000000000000000000000000000000000000000000000000000000002
        f'{hex(from_token_amount.Wei)[2:].zfill(64)}',  # 00000000000000000000000000000000000000000000000000038d7ea4c68000

        f'0x'                                           # 0x
        f'{"1".zfill(64)}'                              # 0000000000000000000000000000000000000000000000000000000000000001
        f'{hex(from_token_amount.Wei)[2:].zfill(64)}'   # 00000000000000000000000000000000000000000000000000038d7ea4c68000
        f'{hex(amount_out_min.Wei)[2:].zfill(64)}'      # 0000000000000000000000000000000000000000000000000000000000224cd1
        f'{"a0".zfill(64)}'                             # 00000000000000000000000000000000000000000000000000000000000000a0
        f'{"".zfill(64)}'                               # 0000000000000000000000000000000000000000000000000000000000000000
        f'{"3".zfill(64)}'                              # 0000000000000000000000000000000000000000000000000000000000000003
        f'{Tokens.WETH[2:].zfill(64)}'                  # 0000000000000000000000005aea5775959fbc2557cc8789bc1bf90a239d9a91
        f'{Tokens.USDT[2:].zfill(64)}'                  # 000000000000000000000000493257fd37edb34451f62edf8d2a0c418852ba4c
        f'{"".zfill(64)}'                               # 0000000000000000000000000000000000000000000000000000000000000000
        f'{Tokens.USDT[2:].zfill(64)}'                  # 000000000000000000000000493257fd37edb34451f62edf8d2a0c418852ba4c
        f'{Tokens.USDC_E[2:].zfill(64)}'                # 0000000000000000000000003355df6d4c9c3035724fd0e3914de96a5a83aaf4
        f'{"1".zfill(64)}'                              # 0000000000000000000000000000000000000000000000000000000000000001
        f'{Tokens.USDC_E[2:].zfill(64)}'                # 0000000000000000000000003355df6d4c9c3035724fd0e3914de96a5a83aaf4
        f'{Tokens.USDC[2:].zfill(64)}'                  # 0000000000000000000000001d17cbcf0d6d143135ae902365d2e5e2a16538d4
        f'{"1".zfill(64)}'                              # 0000000000000000000000000000000000000000000000000000000000000001
    ]

    tx_hash = await client.send_transaction(
        to=router_address,
        data=router_contract.encodeABI('execute',
                                       args=(
                                           '0x0b08',
                                           inputs,
                                           int(time.time() + 1200)
                                       )),
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

