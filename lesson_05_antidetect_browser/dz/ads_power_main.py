import asyncio

from playwright.async_api import async_playwright

from ads_power.client import Client
import config


async def main():
    user_id = 'kq2kc44'
    ads_power_client = Client(api_key=config.ADS_API_KEY, api_uri=config.ADS_API_URI)
    profile_data = ads_power_client.browser.open_browser(user_id=user_id)
    print(profile_data)

    '''
    {
        "code": 0,
        "msg": "success",
        "data": {
            "ws": {
                "puppeteer": "ws://127.0.0.1:58299/devtools/browser/922320e5-1e5e-4c4d-b44e-b45d46dbbfbf",
                "selenium": "127.0.0.1:58299"
            },
            "debug_port": "58299",
            "webdriver": "/Users/riocrash/Library/Application Support/adspower_global/cwd_global/chrome_127/chromedriver.app/Contents/MacOS/chromedriver"
        }
    }
    '''

    async with async_playwright() as p:
        # browser = await p.chromium.launch(headless=False)
        # page = await browser.new_page()
        # await asyncio.sleep(10)

        # browser = await p.chromium.connect(profile_data['data']['ws']['puppeteer'])
        browser = await p.chromium.connect_over_cdp(profile_data['data']['ws']['puppeteer'])
        print(browser.contexts)
        context = browser.contexts[0]

        page = await context.new_page()
        await page.goto('https://app.meteora.ag/')


if __name__ == '__main__':
    asyncio.run(main())
