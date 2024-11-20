import requests

import config


# endpoint = '/status'
# status = requests.get(
#     config.ADS_API_URI
# )
# print(status.json())  # {'code': 0, 'msg': 'success'}

endpoint = '/api/v1/browser/start'
status = requests.get(
    config.ADS_API_URI + endpoint,
    params={
        'user_id': 'kom6u5g'
    }
)
print(status.json())  # {'code': 0, 'msg': 'success', 'data': {'ws': {'puppeteer': 'ws://127.0.0.1:51835/devtools/browser/622e98fb-770f-40be-b8b7-781759944bd4', 'selenium': '127.0.0.1:51835'}, 'debug_port': '51835', 'webdriver': '/Users/riocrash/Library/Application Support/adspower_global/cwd_global/chrome_127/chromedriver.app/Contents/MacOS/chromedriver'}}

