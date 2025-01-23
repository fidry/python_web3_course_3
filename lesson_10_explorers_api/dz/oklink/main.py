import asyncio

from oklink.fundamental_blockchain_data import APIFunctions
from oklink.sol_data import APIFunctions as APIFunctionsSolana
from oklink import config


async def main():
    api_oklink = APIFunctions(url='https://www.oklink.com', key=config.OKLINK_API_KEY)

    # print(await api_oklink.fundamental_data.summary('sui'))
    # print(await api_oklink.fundamental_data.info())
    # print(await api_oklink.fundamental_data.fee('eth'))

    # print(await api_oklink.address.address_details(address='0x32400084C286CF3E17e7B677ea9583e60a000324'))

    # print(await api_oklink.address.token_balance(
    #     address='0x32400084C286CF3E17e7B677ea9583e60a000324',
    #     protocol_type='token_20',
    # ))
    #
    # print()
    # print(await api_oklink.address.token_balance(
    #     address='0x32400084C286CF3E17e7B677ea9583e60a000324',
    #     protocol_type='token_721',
    # ))
    #
    # print()
    # print(await api_oklink.address.token_balance(
    #     address='0x32400084C286CF3E17e7B677ea9583e60a000324',
    #     protocol_type='token_1155',
    # ))

    # res = await api_oklink.address.txlist(
    #     address='0x32400084C286CF3E17e7B677ea9583e60a000324'
    # )
    # print(res)
    # print(len(res))

    # res = await api_oklink.address.txlist_all(
    #     address='0x32400084C286CF3E17e7B677ea9583e60a000324'
    # )
    # print(res)
    # print(len(res))

    # res = await api_oklink.address.find_txs(
    #     address='0x36F302d18DcedE1AB1174f47726E62212d1CcEAD',
    #     signature='0x7ff36ab5',
    #     chain='zksync'
    # )
    # for i in res:
    #     print(i)
    # print(len(res))

    # ------------------------------------- solana -------------------------------------
    # api_oklink = APIFunctionsSolana(url='https://www.oklink.com', key=config.OKLINK_API_KEY)

    # print(await api_oklink.chain_info.info())
    # print(await api_oklink.block_data.block_list())
    # print(await api_oklink.tx_data.sol_balance_change(
    #     tx_hash='4TwJ7MkkUxLdaSz9FKxSQzbEbrJ2eVja71Atqd9vRhSLcF43ngHBiQYdK9M48SKweVhgYVFuomaZHjJr8r86YdWY'))
    # print(await api_oklink.tx_data.tx_details(
    #     tx_hash='4TwJ7MkkUxLdaSz9FKxSQzbEbrJ2eVja71Atqd9vRhSLcF43ngHBiQYdK9M48SKweVhgYVFuomaZHjJr8r86YdWY'))
    # print(await api_oklink.tx_data.tx_list())

    # print(await api_oklink.tx_data.tx_list())

    # print(await api_oklink.account_data.balance_list(
    #     address='A4zodtkK7whbQHfTSmJdRnHVhq9WHgZr7WbC4EPLcJQ7',
    #     protocol_type='nft'
    # ))

    # print(await api_oklink.account_data.account_type(
    #     address='A4zodtkK7whbQHfTSmJdRnHVhq9WHgZr7WbC4EPLcJQ7',
    # ))

    # print(await api_oklink.account_data.get_sol_balance(
    #     address='A4zodtkK7whbQHfTSmJdRnHVhq9WHgZr7WbC4EPLcJQ7',
    # ))


asyncio.run(main())
