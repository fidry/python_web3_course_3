import random
from functools import partial

from loguru import logger

from oklink.fundamental_blockchain_data import APIFunctions
from okx.withdrawal import okx_withdraw_evm

from py_okx_async.models import Chains
from tasks.controller import Controller
from data.models import Settings, Contracts
from utils.db_api.models import Wallet


async def select_random_action(controller: Controller, wallet: Wallet, initial: bool = False):
    settings = Settings()

    possible_actions = []
    weights = []

    swaps = 0
    mints_nft = 0

    eth_balance = await controller.client.balance()

    if float(eth_balance.Ether) < settings.minimal_balance:
        if not settings.okx.allow_withdrawal_from_exchange:
            return 'Insufficient balance'
        return partial(okx_withdraw_evm, Chains.zkSyncEra, 'ETH', controller.client.account.address)

    if initial:
        api_oklink = APIFunctions(url='https://www.oklink.com', key=settings.oklink_api_key)
        txs_lst = await api_oklink.address.txlist_all(
            address=controller.client.account.address,
            chain='zksync'
        )
        swaps = await controller.count_swaps(txs_lst=txs_lst)
        mints_nft = await controller.count_mints_nft(txs_lst=txs_lst)
        logger.debug(
            f'{wallet.address} | amount swaps: {swaps}/{wallet.number_of_swaps}; '
            f'amount mits nft: {mints_nft}/{wallet.number_of_mint_nft}; '
        )

        if swaps >= wallet.number_of_swaps and mints_nft >= wallet.number_of_mint_nft:
            return 'Processed'

#     sufficient_balance = float(eth_balance.Ether) > settings.minimal_balance + settings.eth_amount_for_swap.to_
#     usdc_balance = await controller.client.wallet.balance(token=Contracts.USDC)
#     busd_balance = await controller.client.wallet.balance(token=Contracts.ceBUSD)
#     usdt_balance = await controller.client.wallet.balance(token=Contracts.USDT)
#     wbtc_balance = await controller.client.wallet.balance(token=Contracts.WBTC)
#     # print(f'Balances: eth: {eth_balance.Ether}; usdc: {usdc_balance.Ether}; '
#     #       f'busd: {busd_balance.Ether}; usdt: {usdt_balance.Ether}; wbtc: {wbtc_balance.Ether}')
#
#     if swaps < wallet.number_of_swaps:
#         if usdc_balance.Wei:
#             possible_actions += [
#                 controller.maverick.swap_usdc_to_eth,
#                 controller.mute.swap_usdc_to_eth,
#                 controller.space_fi.swap_usdc_to_eth,
#                 controller.syncswap.swap_usdc_to_eth,
#             ]
#             weights += [
#                 1,
#                 1,
#                 1,
#                 1,
#             ]
#
#         if busd_balance.Wei:
#             possible_actions += [
#                 controller.maverick.swap_busd_to_eth,
#                 controller.space_fi.swap_busd_to_eth,
#                 controller.syncswap.swap_busd_to_eth,
#             ]
#             weights += [
#                 1,
#                 1,
#                 1,
#             ]
#
#         if usdt_balance.Wei:
#             possible_actions += [
#                 controller.space_fi.swap_usdt_to_eth,
#                 controller.syncswap.swap_usdt_to_eth,
#             ]
#             weights += [
#                 1,
#                 1,
#             ]
#
#         if wbtc_balance.Wei:
#             possible_actions += [
#                 controller.mute.swap_wbtc_to_eth,
#                 controller.space_fi.swap_wbtc_to_eth,
#                 controller.syncswap.swap_wbtc_to_eth,
#             ]
#             weights += [
#                 1,
#                 1,
#                 1,
#             ]
#
#         if sufficient_balance:
#             possible_actions += [
#                 controller.maverick.swap_eth_to_usdc,
#                 controller.maverick.swap_eth_to_busd,
#                 controller.mute.swap_eth_to_usdc,
#                 controller.mute.swap_eth_to_wbtc,
#                 controller.space_fi.swap_eth_to_usdc,
#                 controller.space_fi.swap_eth_to_usdt,
#                 controller.space_fi.swap_eth_to_busd,
#                 controller.space_fi.swap_eth_to_wbtc,
#                 controller.syncswap.swap_eth_to_usdc,
#                 controller.syncswap.swap_eth_to_usdt,
#                 controller.syncswap.swap_eth_to_busd,
#                 controller.syncswap.swap_eth_to_wbtc,
#             ]
#             weights += [
#                 1,
#                 1,
#                 1,
#                 1,
#                 1,
#                 1,
#                 1,
#                 1,
#                 1,
#                 1,
#                 1,
#                 1,
#             ]
#
#     if dmail < wallet.number_of_dmail:
#         if float(eth_balance.Ether) > settings.minimal_balance:
#             possible_actions += [
#                 controller.dmail.send_dmail,
#             ]
#             weights += [
#                 5,
#             ]
#
#     if possible_actions:
#         action = None
#         while not action:
#             action = random.choices(possible_actions, weights=weights)[0]
#
#         else:
#             return action
#
#     return None
