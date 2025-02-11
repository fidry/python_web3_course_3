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
    dmail = 0

    eth_balance = await controller.client.balance()
    usdc_e_balance = await controller.client.balance(token_address=Contracts.USDC_E.address)
    usdt_balance = await controller.client.balance(token_address=Contracts.USDT.address)

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
        dmail = await controller.count_dmail(txs_lst=txs_lst)
        logger.info(
            f'{wallet.address} | amount swaps: {swaps}/{wallet.number_of_swaps}; '
            f'amount mits nft: {mints_nft}/{wallet.number_of_mint_nft}; '
            f'amount dmail: {dmail}/{wallet.number_of_dmail}; '
        )

        if swaps >= wallet.number_of_swaps and mints_nft >= wallet.number_of_mint_nft:
            return 'Processed'

    sufficient_balance_for_swap = float(eth_balance.Ether) > settings.minimal_balance + settings.eth_amount_for_swap.to_
    if swaps < wallet.number_of_swaps:
        if sufficient_balance_for_swap:
            possible_actions += [
                controller.space_fi.swap_eth_to_usdt,
                controller.space_fi.swap_eth_to_wbtc,
                controller.koi_finance.swap_eth_to_usdc,
            ]

            weights += [
                1,
                1,
                1,
            ]

        if usdc_e_balance.Wei:
            possible_actions += [
                controller.space_fi.swap_usdc_e_to_eth,
                controller.syncswap.swap_usdc_e_to_eth,
            ]

            weights += [
                1,
                1,
            ]

        if usdt_balance.Wei:
            possible_actions += [
                controller.space_fi.swap_usdt_to_eth,
                controller.space_fi.swap_usdt_to_usdc_e,
            ]

            weights += [
                1,
                1,
            ]

    if float(eth_balance.Ether) > settings.minimal_balance and mints_nft < wallet.number_of_mint_nft:
        possible_actions += [
            controller.whale_nft.mint,
        ]

        weights += [
            0.5,
        ]

    if float(eth_balance.Ether) > settings.minimal_balance and dmail < wallet.number_of_dmail:
        possible_actions += [
            controller.dmail.send_dmail,
        ]

        weights += [
            1,
        ]

    if possible_actions:
        action = random.choices(possible_actions, weights=weights)[0]
        return action

    return None
