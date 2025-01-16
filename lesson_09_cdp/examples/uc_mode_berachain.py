from seleniumbase import SB

from config import PROXY


# UC mode is not working. Our connection being detected as a bot.

# with SB(uc=False, test=True, proxy=PROXY) as sb:
#     url = "https://bartio.faucet.berachain.com/"
#     sb.open(url)
#     sb.sleep(1)
#     sb.click('//*[@id="terms"]', by="xpath")
#     sb.sleep(1)
#     sb.click('button:contains("I AGREE")')
#     sb.scroll_to_top()

#     sb.sleep(1111)
    

# UC mode is on. Captcha successfully passed

# with SB(uc=True, test=True, proxy=PROXY) as sb:
#     url = "https://bartio.faucet.berachain.com/"
#     sb.uc_open_with_reconnect(url, 9)

#     sb.uc_click('//*[@id="terms"]', by="xpath", timeout=2, reconnect_time=None)
#     sb.sleep(1)
#     sb.uc_click('button:contains("I AGREE")', timeout=2, reconnect_time=None)
#     sb.sleep(1)
    
#     sb.press_keys(
#         '/html/body/div[2]/main/div/div[1]/div[1]/div[2]/div[2]/div/input',
#         by="xpath",
#         text='0xeACFA4278397B2A57E8A098CC86909b49335Cb1B'
#         )
    
#     sb.sleep(1)
#     sb.uc_click('button:contains("Drip Tokens")', timeout=2, reconnect_time=None)
    
#     sb.sleep(10111)
    
# UC mode is on with CDP mode. Captcha successfully passed
with SB(uc=True, test=True, proxy=PROXY) as sb:
    url = "https://bartio.faucet.berachain.com/"
    
    sb.activate_cdp_mode(url)
    sb.sleep(1.5)

    sb.cdp.click_if_visible('//*[@id="terms"]')
    sb.sleep(1)
    
    sb.cdp.click_if_visible('button:contains("I AGREE")')
    sb.sleep(5)
    
    sb.cdp.press_keys(
        '/html/body/div[2]/main/div/div[1]/div[1]/div[2]/div[2]/div/input',
        text='0xeACFA4278397B2A57E8A098CC86909b49335Cb1B'
        )

    sb.sleep(1)
    sb.cdp.click_if_visible('button:contains("Drip Tokens")')
    
    
    sb.sleep(10111)


'''
Ключевые параметры SeleniumBase для антидетекта и 
обхода обнаружения автоматизации

undetectable (или короткие версии: uc, undetected)
Использует undetected-chromedriver для обхода обнаружения ботов
Самый важный параметр для антидетекта

user_agent
Позволяет изменить User-Agent браузера

disable_csp
Отключает политику безопасности контента на сайтах
Может помочь обойти некоторые защиты

incognito
Включает режим инкогнито в Chromium браузерах
Помогает избежать отслеживания через cookies/кэш

proxy
Позволяет использовать прокси
Формат: "SERVER:PORT" или "USER:PASS@SERVER:PORT"

disable_cookies
Отключает cookies на сайтах

do_not_track
Отправляет сигнал "Do Not Track" сайтам

use_auto_ext
Отключает использование стандартного расширения автоматизации Chrome
'''