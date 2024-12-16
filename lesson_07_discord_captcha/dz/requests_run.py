import asyncio
import json

from loguru import logger

import requests
from playwright.async_api import async_playwright

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

headers = {
    'authority': 'lizlounge.io',
    'accept': 'text/x-component',
    'accept-language': 'ru',
    'content-type': 'text/plain;charset=UTF-8',
    'next-action': '11abf0d5b9b4856af4cc7efe5faaf09e69caeadb',
    'next-router-state-tree': '%5B%22%22%2C%7B%22children%22%3A%5B%5B%22locale%22%2C%22en%22%2C%22d%22%5D%2C%7B'
                              '%22children%22%3A%5B%22('
                              'app)%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%2C%22%2F%22%2C%22refresh%22'
                              '%5D%7D%2Cnull%2Cnull%2Ctrue%5D%7D%5D%7D%5D',
    'origin': 'https://lizlounge.io',
    'referer': 'https://lizlounge.io/',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/122.0.0.0 Safari/537.36',
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


async def main():
    async with async_playwright() as p:
        profile_data = await get_profile_data(private_key=private_key)
        browser = await p.chromium.connect_over_cdp(profile_data['data']['ws']['puppeteer'],
                                                    slow_mo=1500, )
        context = browser.contexts[0]
        token, task_id = await capsolver_recaptcha_v3(api_key=capsolver_api_key, data=captcha_data, get_task_id=True)
        logger.info(f'Token: {token}')
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

        context_cookies = await context.cookies(urls='https://lizlounge.io/')

        cookies_ = {'NEXT_LOCALE': '',
                    '_ga': '',
                    '__Host-next-auth.csrf-token': '',
                    '__Secure-next-auth.callback-url': '',
                    '__Secure-next-auth.session-token': '',
                    '_ga_Y5DW2X58Y9': '',
                    }
        for val in context_cookies:
            if val['name'] in cookies_:
                cookies_[val['name']] = val['value']

        logger.debug(f'Received cookie data 🍪: {cookies_}')

        session = requests.session()
        session.headers.update(headers)
        session.cookies.update(cookies_)
        session.proxies.update(proxy)

        while True:

            token, task_id = await capsolver_recaptcha_v3(api_key=capsolver_api_key,
                                                          data=captcha_data,
                                                          get_task_id=True)
            logger.debug(f'Token: {token}')
            logger.debug(f'Task_id: {task_id}')
            if isinstance(token, str):

                data = [{"recaptcha": f"{token}",
                         "email": "sashanikolayewich@gmail.com",
                         "newsletterConsent": "true",
                         "termsConsent": "true"}]

                response = session.post('https://lizlounge.io/', data=json.dumps(data))

                logger.info(f'Status code POST request: {response.status_code}')
                logger.info(f'Text response: {response.text}')

                if "User signed up successfully" in response.text:
                    logger.info('Captcha completed successfully! 🎉')
                    break

                else:
                    await report_result_token(task_id=task_id, api_key=capsolver_api_key, invalid=True)

                    rr = session.get('https://lizlounge.io/api/auth/session')
                    def_cookies = rr.cookies.get_dict()
                    session.cookies.set('__Secure-next-auth.session-token',
                                        def_cookies['__Secure-next-auth.session-token'])
                    await asyncio.sleep(10)

asyncio.run(main())
