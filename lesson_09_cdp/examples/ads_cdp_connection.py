import requests
import asyncio

from playwright.async_api import async_playwright, BrowserContext

# Constants
ADS_ID = "km7e9xd"
ADS_API_URL = "http://local.adspower.net:50325"


async def open_profile() -> BrowserContext:
    open_url = f"{ADS_API_URL}/api/v1/browser/start?user_id={ADS_ID}"
    ads_api_response = requests.get(open_url).json()
    ws_endpoint = ads_api_response['data']['ws']['puppeteer']
    
    async with async_playwright() as pw:
        browser = await pw.chromium.connect_over_cdp(
            endpoint_url=ws_endpoint,
            timeout=1500,
            slow_mo=500
        )
        print(f'connected to {ws_endpoint}')
        

        context = browser.contexts[0]
        page = context.pages[0]
        await page.goto('https://bartio.faucet.berachain.com/')
        await asyncio.sleep(3)
        await asyncio.sleep(3)
        
        
        await asyncio.sleep(3330)
        
        return context

if __name__ == "__main__":
    context = asyncio.run(open_profile())
