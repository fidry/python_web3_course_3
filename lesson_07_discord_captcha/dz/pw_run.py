import asyncio
from loguru import logger

import requests
from playwright.async_api import async_playwright, Page

from my_keys import *

mail = 'sashanikolayewich@gmail.com'
page_url = "https://lizlounge.io/"
site_key = '6LdPDSsqAAAAAKbD20y78gf0lrVKJeNd9LoCNvWI'
action = 'signupFormSubmit'

captcha_data = {
    "clientKey": capsolver_api_key,
    "task": {
        "type": 'ReCaptchaV3Task',
        "websiteKey": site_key,
        "websiteURL": page_url,
        "pageAction": action,
        "proxyType": proxyType,
        "proxyAddress": proxyAddress,
        "proxyPort": proxyPort,
        "proxyLogin": proxyLogin,
        "proxyPassword": proxyPassword
    }
}


async def capsolver_recaptcha_v3(api_key: str, data: dict, get_task_id: bool = False):
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


async def change_recaptcha_token(page: Page, token: str):
    await page.evaluate("""
        (() => {
            function injectExecute() {
                if (window.grecaptcha && window.grecaptcha.execute) {
                    const originalExecute = window.grecaptcha.execute;
                    window.grecaptcha.execute = function() {
                        return Promise.resolve('%s');
                    };
                    return true;
                }
                return false;
            }

            if (!injectExecute()) {
                Object.defineProperty(window, 'grecaptcha', {
                    configurable: true,
                    get: function() {
                        return this._grecaptcha;
                    },
                    set: function(value) {
                        this._grecaptcha = value;
                        if (value && value.execute) {
                            const originalExecute = value.execute;
                            value.execute = function() {
                                return Promise.resolve('%s');
                            };
                        }
                    }
                });
            }
        })();
    """ % (token, token))


async def main():
    async with async_playwright() as p:

        token, task_id = await capsolver_recaptcha_v3(api_key=capsolver_api_key, data=captcha_data, get_task_id=True)
        logger.info(f'Token: {token}')

        profile_data = await get_profile_data(private_key=private_key)
        browser = await p.chromium.connect_over_cdp(profile_data['data']['ws']['puppeteer'],
                                                    slow_mo=1500, )
        context = browser.contexts[0]
        page = await context.new_page()
        await page.evaluate("""
                    // Маскируем автоматизацию
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;

                    // Удаляем следы Playwright
                    delete window.playwright;
                    delete window.selenium;
                    delete window.puppeteer;

                    // Маскируем webdriver
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false
                    });
                """)
        await page.goto('https://lizlounge.io/', timeout=60000)

        if await page.get_by_placeholder('Enter your email').is_visible():
            await page.locator('//*[@id="chakra-modal--body-:r4:"]/form/div[2]/div[1]').click()
            await page.locator('//*[@id="chakra-modal--body-:r4:"]/form/div[3]/div[1]/label[1]').click()
            await page.get_by_placeholder('Enter your email').type(mail)

            await change_recaptcha_token(page=page, token=token)

            sign_up_buttton = page.locator('button:has-text("Sign Up")')

            await sign_up_buttton.click()
            await asyncio.sleep(5)

            if await sign_up_buttton.is_visible():

                while True:
                    await asyncio.sleep(10)
                    await report_result_token(task_id=task_id, api_key=capsolver_api_key, invalid=True)

                    new_token, task_id = await capsolver_recaptcha_v3(api_key=capsolver_api_key,
                                                                      data=captcha_data, get_task_id=True)
                    logger.info(f'New token: {new_token}')

                    if isinstance(new_token, str):
                        await change_recaptcha_token(page=page, token=new_token)
                        await sign_up_buttton.click()

                        if not await sign_up_buttton.is_visible():
                            logger.info("✅Successfully passed captcha!✅")
                            await report_result_token(task_id=task_id,
                                                      api_key=capsolver_api_key,
                                                      invalid=False,
                                                      message='good token')
                            break
            else:
                await report_result_token(task_id=task_id,
                                          api_key=capsolver_api_key,
                                          invalid=False,
                                          message='good token')
            logger.info('🏆Victory is ours! It is unstoppable! 🏆')

asyncio.run(main())
