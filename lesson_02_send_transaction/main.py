import asyncio

from web3 import AsyncWeb3

import config
from client import Client
from data.models import TokenABI


async def main():
    # Задача: сделать апрув всего баланса USDT для uniswap

    token_address = AsyncWeb3.to_checksum_address('<ENTER TOKEN ADDRESS>')
    spender = AsyncWeb3.to_checksum_address('<ENTER SPENDER ADDRESS>')

    client = Client(private_key=config.PRIVATE_KEY, rpc='<ENTER RPC>')

    contract = client.w3.eth.contract(
        address=token_address,
        abi=TokenABI
    )

    decimals = await contract.functions.decimals().call()
    token_balance = await contract.functions.balanceOf(client.account.address).call()
    approved_amount = await contract.functions.allowance(client.account.address, spender).call()

    print('decimals:', decimals)
    print('token_balance:', token_balance / 10 ** decimals)
    print('approved_amount:', approved_amount / 10 ** decimals)

    if approved_amount < token_balance:
        tx_hash = await client.send_transaction(
            to=token_address,
            data=contract.encodeABI('approve',
                                    args=(
                                        spender,
                                        token_balance
                                    )),
            max_priority_fee_per_gas=0
        )
        if tx_hash:
            try:
                await client.verif_tx(tx_hash=tx_hash)
                print(f'Transaction success!! tx_hash: {tx_hash.hex()}')
            except Exception as err:
                print(f'Transaction error!! tx_hash: {tx_hash.hex()}; error: {err}')
        else:
            print(f'Transaction error!!')
    else:
        print('Already approved')


if __name__ == '__main__':
    asyncio.run(main())
