import asyncio
import pickle
from typing import Any

from playwright.async_api import async_playwright

from ads_power.client import Client
from ads_power.data.models import Proxy
import config


def export_cookies(cookies: list[dict[str, str]] | Any, to_path: str = 'cookies.dat') -> None:
    with open(to_path, 'wb') as f:
        pickle.dump(cookies, f)


def import_cookies(from_path: str = 'cookies.dat') -> list[dict[str, str]] | Any:
    with open(from_path, 'rb') as f:
        cookies = pickle.load(f)
    return cookies


async def main():
    ads_power_client = Client(api_key=config.ADS_API_KEY, api_uri=config.ADS_API_URI)
    profile_1 = ads_power_client.profiles.new_profile(
        group_name='test',
        proxy=Proxy(),
        name='test_cookies'
    )
    profile_1_id = profile_1.get('data', {}).get('id')
    profile_1_data = ads_power_client.browser.open_browser(user_id=profile_1_id)
    await asyncio.sleep(3)

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(profile_1_data['data']['ws']['puppeteer'])
        context = browser.contexts[0]

        page = await context.new_page()
        await page.goto('https://stackoverflow.com/')
        await page.locator('#onetrust-accept-btn-handler').click()
        await asyncio.sleep(1)

        cookies = await context.cookies()
        export_cookies(cookies=cookies)
        ads_power_client.browser.close_browser(user_id=profile_1_id)

        await asyncio.sleep(3)

    cookies = import_cookies()
    for cookie in cookies:
        print(cookie)
    print()

    profile_2 = ads_power_client.profiles.new_profile(
        group_name='test',
        proxy=Proxy(),
        name='test_cookies2',
        cookie=str(cookies)
    )
    print(profile_2)

if __name__ == '__main__':
    asyncio.run(main())
