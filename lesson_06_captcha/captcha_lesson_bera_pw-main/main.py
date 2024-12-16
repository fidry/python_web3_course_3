import asyncio
from playwright.async_api import async_playwright

from my_keys import adspower_api_url, adspower_api_key, private_key, api_key
from anticaptchaofficial.turnstileproxyless import *


async def get_profile_data(private_key: str) -> dict:
    """Запрашивает и возвращает данные профиля в виде словаря."""
    response = requests.get(adspower_api_url, params={
        "user_id": private_key,
        "apikey": adspower_api_key
    })
    data = response.json()
    # print(data)

    if data["code"] != 0:
        raise Exception(f"Не удалось получить данные профиля: {data['msg']}")

    return data


async def main():
    async with async_playwright() as p:
        profile_data = await get_profile_data(private_key=private_key)

        browser = await p.chromium.connect_over_cdp(profile_data['data']['ws']['puppeteer'],
                                                    slow_mo=2000,
                                                    # headers=headers,
                                                    )

        solver = turnstileProxyless()
        solver.set_verbose(1)
        solver.set_key(api_key)
        solver.set_website_url("https://bartio.faucet.berachain.com/")
        solver.set_website_key("0x4AAAAAAARdAuciFArKhVwt")

        token = solver.solve_and_return_solution()
        if token != 0:
            print("token: " + token)
        else:
            print("task finished with error " + solver.error_code)

        context = browser.contexts[0]
        page = await context.new_page()
        await page.goto('https://bartio.faucet.berachain.com/')
        await asyncio.sleep(3)

        await page.evaluate(f"""
                var input = document.querySelector('input[name="cf-turnstile-response"]');
                input.setAttribute('value', '{token}');
            """)

        await asyncio.sleep(3)

        await page.locator('input').first.fill(
            '0x3dfe703ff5492Ad0053c8d56De5f7C515018F8CE')
        await asyncio.sleep(3)

        if await page.locator('button:has-text("Drip Tokens")').is_visible():
            await page.locator('button:has-text("Drip Tokens")').click()


asyncio.run(main())
