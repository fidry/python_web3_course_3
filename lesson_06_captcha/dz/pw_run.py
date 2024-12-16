import asyncio
import requests

from loguru import logger
from playwright.async_api import async_playwright

from my_keys import adspower_api_url, adspower_api_key, capsolver_api_key, private_key_7

site_key = '6LeeT-0pAAAAAFJ5JnCpNcbYCBcAerNHlkK4nm6y'
page_url = 'https://app.getgrass.io/register?referralCode=GRASS'

payload_captcha = {
    "clientKey": capsolver_api_key,
    "task": {
        "type": 'ReCaptchaV2TaskProxyLess',
        "websiteKey": site_key,
        "websiteURL": page_url,
    }
}


async def capsolver_recaptcha_v2(api_key: str, data: dict, get_task_id: bool = False):
    """
    :param api_key: Your API key from the Capsolver account.
    :param data: The data sent to the Capsolver API to solve the captcha.
    :param get_task_id: Set to `True` if you need to return the ID of the request for use elsewhere.
    """

    res = requests.post("https://api.capsolver.com/createTask", json=data)
    resp = res.json()
    task_id = resp.get("taskId")
    if not task_id:
        logger.error(f'Failed to create task: {res.text}')
        return
    logger.info(f"⏳Got taskId: {task_id} / Getting result...⏳")

    while True:
        await asyncio.sleep(1)  # delay
        payload = {"clientKey": api_key, "taskId": task_id}
        res = requests.post("https://api.capsolver.com/getTaskResult", json=payload)
        resp = res.json()
        status = resp.get("status")
        if status == "ready":
            token = str(resp.get("solution", {}).get('gRecaptchaResponse'))
            if get_task_id:
                return token, task_id
            else:
                return token

        if status == "failed" or resp.get("errorId"):
            logger.info(f'Solve failed! response: {res.text}')
            return


async def report_result_token(task_id: str, api_key: str, invalid: bool, message: str = 'invalid token'):
    """
    :param task_id: The ID of the solving request.
    :param api_key: Your API key from the Capsolver account.
    :param invalid: Indicates if the token is valid. `True` means the token is invalid, `False` means it's valid.
    :param message: A status message, either 'invalid token' or 'good token'.
    """
    data = {
        "clientKey": api_key,
        "taskId": task_id,
        "result": {
            "invalid": invalid,  # // true, false  Whether the results of task processing
            "code": 1001,
            "message": message
        }
    }
    rr = requests.post('https://api.capsolver.com/feedbackTask', json=data)
    logger.info(f'Feedback received ℹ️: {rr.json()}')


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

        profile_data = await get_profile_data(private_key=private_key_7)

        browser = await p.chromium.connect_over_cdp(profile_data['data']['ws']['puppeteer'],
                                                    slow_mo=2500,
                                                    )

        context = browser.contexts[0]
        page = await context.new_page()
        await page.goto(page_url)

        token = await capsolver_recaptcha_v2(api_key=capsolver_api_key, data=payload_captcha)
        print(token)

        # await page.wait_for_function("window.___grecaptcha_cfg !== undefined")
        #
        # result = await page.evaluate(
        #     f"""() => window.___grecaptcha_cfg.clients['0']['U']['U']['callback']('{token}')"""
        # )
        # print("Result:", result)

        await page.get_by_placeholder('Email').type('cryptomuro001@gmail.com')
        await page.get_by_placeholder('Username').type('Crytpmuro00001')
        await page.get_by_placeholder('Password').first.type('Howtocodepython2024.')
        await page.get_by_placeholder('Confirm Password').last.type('Howtocodepython2024.')
        await page.locator('p:has-text("I agree to the")').click()
        await page.locator('p:has-text("I agree to receive updates about products and services, '
                           'promotions, special offers, news & events from Grass.")').click()

        await page.wait_for_function("window.___grecaptcha_cfg !== undefined")

        await page.evaluate(
            f"""() => window.___grecaptcha_cfg.clients['0']['U']['U']['callback']('{token}')"""
        )

        await page.locator('button:has-text("REGISTER")').click()

asyncio.run(main())
