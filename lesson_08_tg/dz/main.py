import asyncio

from loguru import logger

from ads_power.client import Client as AdsPowerClient
import config
from controllers.blum_controller import BlumPageController


async def main():
    ads_power_client: AdsPowerClient = AdsPowerClient(
        api_key=config.ADS_API_KEY,
        api_uri=config.ADS_API_URI,
    )

    # Получаем группу с названием "Telegram"
    telegram_group_id = ads_power_client.groups.get_group_id_by_group_name(
        group_name='Telegram',
    )

    # Получаем все профили в группе "Telegram"
    telegram_profiles: dict = ads_power_client.profiles.query_profile(
        group_id=telegram_group_id,
    )
    if not telegram_profiles:
        raise RuntimeError('Профили в группе "Telegram" не найдены')

    for profile in telegram_profiles['data']['list']:
        user_id: str = profile['user_id']
        profile_name: str = profile['name']
        start_profile_data: dict = ads_power_client.browser.open_browser(
            user_id=user_id,
        )

        try:
            await asyncio.sleep(3)

            async with BlumPageController(
                    cdp_url=start_profile_data['data']['ws']['puppeteer'],
                    profile_name=profile_name,
            ) as blum_controller:
                await blum_controller.handle_account()

                await asyncio.sleep(5)

        except Exception as error:
            logger.exception('Во время работы браузера произошла ошибка', error)

        ads_power_client.browser.close_browser(user_id=user_id)


if __name__ == '__main__':
    asyncio.run(main())
