import asyncio

import requests
from playwright.async_api import async_playwright

import config


async def main():
    profile_id = '488330839'

    open_profile_url = f'{config.DOLPHIN_API_URI}/v1.0/browser_profiles/{profile_id}/start?automation=1'
    profile_data = requests.get(open_profile_url).json()

    ws_endpoint = profile_data['automation']['wsEndpoint']
    port = profile_data['automation']['port']

    async with async_playwright() as p:
        # endpoint = f'ws://localhost:{port}{ws_endpoint}'
        endpoint = f'ws://127.0.0.1:{port}{ws_endpoint}'
        browser = await p.chromium.connect_over_cdp(endpoint)
        print(browser.contexts)
        context = browser.contexts[0]

        page = await context.new_page()
        await page.goto('https://app.meteora.ag/')


if __name__ == '__main__':
    asyncio.run(main())
