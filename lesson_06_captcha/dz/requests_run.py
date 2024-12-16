import asyncio

import requests
from anycaptcha import Solver, Service
from fake_useragent import FakeUserAgent
from my_keys import two_captcha_key, proxy_6

site_key = '6LeeT-0pAAAAAFJ5JnCpNcbYCBcAerNHlkK4nm6y'
page_url = 'https://app.getgrass.io/register?referralCode=r4MuY0noBROwL1R'

headers = {
    'authority': 'api.getgrass.io',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ru',
    'content-type': 'application/json',
    'origin': 'https://app.getgrass.io',
    'referer': 'https://app.getgrass.io/',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': FakeUserAgent().random,
}


async def main():
    solver = Solver(Service.TWOCAPTCHA, api_key=two_captcha_key)
    solv_captcha = await solver.solve_recaptcha_v2(site_key=site_key,
                                                   page_url=page_url,
                                                   is_enterprise=True)
    solv_result = solv_captcha.solution.as_dict()

    token = solv_result['token']
    print(token)

    json_data = {
        'email': 'liliya28121999@gmail.com',
        'password': 'Liliya902375.',
        'role': 'USER',
        'referralCode': 'GRASS',
        'username': 'Liliya_ne_liliya',
        'marketingEmailConsent': True,
        'recaptchaToken': token,
        'listIds': [
            15,
        ],
    }

    print(json_data)

    response = requests.post('https://api.getgrass.io/register', headers=headers, json=json_data, proxies=proxy_6)
    print(response)
    print(response.text)


asyncio.run(main())
