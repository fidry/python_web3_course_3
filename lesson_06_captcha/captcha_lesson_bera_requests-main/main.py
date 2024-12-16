import requests

from fake_useragent import FakeUserAgent
from anticaptchaofficial.turnstileproxyless import turnstileProxyless

from my_keys import wallet, api_key, proxy

params = {
    'address': f'{wallet}',
}

data = {"address": f"{wallet}"}

solver = turnstileProxyless()
solver.set_verbose(1)
solver.set_key(api_key)
solver.set_website_url('https://bartio.faucet.berachain.com/')
solver.set_website_key("0x4AAAAAAARdAuciFArKhVwt")

# await asyncio.sleep(15)
g_response = solver.solve_and_return_solution()
if g_response != 0:
    print("g-response: " + g_response)

headers = {
    'authority': 'bartiofaucet.berachain.com',
    'accept': '*/*',
    'accept-language': 'ru',
    'authorization': f'Bearer {g_response}',
    'content-type': 'text/plain;charset=UTF-8',
    'origin': 'https://bartio.faucet.berachain.com',
    'referer': 'https://bartio.faucet.berachain.com/',
    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'sec-ch-ua-mobile': '?0',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': FakeUserAgent().random,
}

# # Запрос с ошибкой
# response_not = requests.post('https://bartiofaucet.berachain.com/api/claim',
#                              json=params,
#                              headers=headers,
#                              data=data,
#                              proxies=proxy)
# print(response_not.text)  # в таких случаях можете написать в Chatgpt или Google и он вам скажет что у вас не так

# Правильный запрос
response = requests.post('https://bartiofaucet.berachain.com/api/claim', json=params, headers=headers, proxies=proxy)
print(response.text)




































