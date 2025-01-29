import random
import asyncio
from datetime import datetime

from loguru import logger
from sqlalchemy import select, func

from client import Client
from data.models import Settings
from utils.db_api.wallet_api import db
from utils.db_api.models import Wallet
from tasks.controller import Controller
from functions.select_random_action import select_random_action
from utils.update_expired import update_expired, update_next_action_time


async def activity():
    settings = Settings()
    delay = 10

    update_expired(initial=False)
    await asyncio.sleep(5)

    while True:
        try:
            now = datetime.now()

            wallet: Wallet = db.one(
                Wallet, Wallet.initial_completed.is_(True) & (Wallet.next_activity_action_time <= now)
            )

            if not wallet:
                await asyncio.sleep(delay)
                continue

            eth_client = Client(rpc=settings.rpc_eth, proxy=wallet.proxy)
            await eth_client.wait_for_acceptable_gas(acceptable_gas_price_gwei=settings.maximum_gas_price, sleep=60)

            zksync_client = Client(rpc=settings.rpc_zksync, private_key=wallet.private_key, proxy=wallet.proxy)
            controller = Controller(client=zksync_client)

            action = await select_random_action(controller=controller, wallet=wallet, initial=False)

            if not action:
                logger.error(f'{wallet.address} | select_random_action | can not choose the action')
                update_next_action_time(
                    private_key=wallet.private_key, seconds=settings.delay_in_case_of_error, initial=False)
                continue

            if action == 'Insufficient balance':
                logger.error(f'{wallet.address}: Insufficient balance')
                update_next_action_time(
                    private_key=wallet.private_key, seconds=settings.delay_in_case_of_error, initial=False)
                continue

            status = await action()

            if 'Failed' not in status:
                update_next_action_time(
                    private_key=wallet.private_key,
                    seconds=random.randint(settings.activity_actions_delay.from_, settings.activity_actions_delay.to_),
                    initial=False
                )

                logger.success(f'{wallet.address}: {status}')

                stmt = select(func.min(Wallet.next_activity_action_time)).where(Wallet.initial_completed.is_(True))
                next_action_time = db.one(stmt=stmt)

                logger.info(f'The next closest activity action will be performed at {next_action_time}')

                await asyncio.sleep(delay)

            else:
                update_next_action_time(
                    private_key=wallet.private_key, seconds=settings.delay_in_case_of_error, initial=False)
                logger.error(f'{wallet.address}: {status}')

        except BaseException as e:
            logger.exception(f'Something went wrong: {e}')

        finally:
            await asyncio.sleep(delay)
