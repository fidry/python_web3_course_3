import json
import asyncio
import random

import requests
from loguru import logger

from anycaptcha import Solver, Service
from anycaptcha import CaptchaCharType
from websockets_proxy import proxy_connect, Proxy

from config import headers_interaction, pandez_bot_id, uri, payload, post_data, interaction_post_url
from functions import press_buttons, send_captcha_digits
from my_keys import twocaptcha_apikey, proxy_15_full, proxy_15

user_agent_ws = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                 "Chrome/122.0.0.0 Safari/537.36")


async def main():
    # async with websockets.connect(uri, user_agent_header=user_agent_ws) as websocket:
    proxy = Proxy.from_url(proxy_15_full)
    async with proxy_connect(uri, proxy=proxy, user_agent_header=user_agent_ws) as websocket:

        logger.debug('✨ Discord WebSocket Gateway connection established successfully')
        await websocket.send(json.dumps(payload))

        session_id = None
        session_ids = []
        verify_button_pressed = False
        message_id = None
        captcha_solved = False

        with requests.session() as session:
            session.proxies.update(proxy_15)
            session.headers.update(headers_interaction)

            async for event in websocket:
                event = json.loads(event)
                logger.info(f'Message: {event}')

                await asyncio.sleep(5)

                if event['t'] == 'READY' and not verify_button_pressed:
                    for i in event['d']['sessions']:
                        if i['status'] == 'online':
                            session_ids.append(i['session_id'])

                    if len(session_ids) == 1:
                        session_id = session_ids[0]
                    else:
                        session_id = session_ids[-1]

                    logger.debug(f'📊 Active session IDs registry: {session_ids}')
                    logger.debug(f'🔐 Active session identifier: {session_id}')

                    await asyncio.sleep(3)

                    await press_buttons(url=interaction_post_url,
                                        session=session,
                                        session_id=session_id,
                                        custom_id='verify',
                                        data=post_data)
                    verify_button_pressed = True  # Устанавливаем флаг после нажатия кнопки

                elif event['t'] == "SESSIONS_REPLACE" and not verify_button_pressed:
                    session_id = event['d'][0]['session_id']
                    logger.debug("Replace_session:", session_id)
                    await press_buttons(url=interaction_post_url,
                                        session=session,
                                        session_id=session_id,
                                        custom_id='verify',
                                        data=post_data)

                    verify_button_pressed = True  # Устанавливаем флаг после нажатия кнопки

                """осталось continue отправлять запросы через interaction """

                if event["t"] == "MESSAGE_CREATE":
                    try:
                        if event['d']['webhook_id'] == pandez_bot_id:
                            message_id = event['d']['id']
                            logger.debug(f'🏷️ Current message ID: {message_id}')
                            await asyncio.sleep(2)
                            await press_buttons(url=interaction_post_url,
                                                session=session,
                                                session_id=session_id,
                                                message_id=message_id,
                                                custom_id='turnOffDMContinue',
                                                data=post_data)
                    except KeyError:
                        pass

                if event['t'] == 'MESSAGE_UPDATE' and not captcha_solved:
                    try:
                        if event['d']['webhook_id'] == pandez_bot_id:
                            if 'thumbnail' in event['d']['embeds'][0]:
                                await press_buttons(url=interaction_post_url,
                                                    session=session,
                                                    session_id=session_id,
                                                    message_id=message_id,
                                                    custom_id='readRulesContinue',
                                                    data=post_data)

                            elif 'title' in event['d']['embeds'][0]:
                                captcha_img_url = event['d']['embeds'][0]['image']['url']
                                logger.debug(f'📸 Source captcha image: {captcha_img_url}')

                                if captcha_img_url:
                                    img_bytes = requests.get(captcha_img_url).content

                                if isinstance(img_bytes, bytes):
                                    while True:
                                        solver = Solver(Service.TWOCAPTCHA, api_key=twocaptcha_apikey)
                                        solved = await solver.solve_image_captcha(
                                            image=img_bytes,  # it can be a Path, file-object or bytes.
                                            char_type=CaptchaCharType.NUMERIC,  # optional
                                            is_phrase=False,  # optional
                                            is_case_sensitive=False,  # optional
                                            is_math=False,  # optional
                                            min_len=6,  # optional
                                            max_len=6,  # optional
                                            comment='The image contains 6 green numbers'  # optional
                                        )
                                        captcha_solution_result = solved.solution.as_dict()

                                        print(captcha_solution_result)

                                        captcha_solution = captcha_solution_result['text']

                                        logger.info(f'🔍 Generated captcha solution: {captcha_solution}')

                                        if len(captcha_solution) == 6 and captcha_solution.isdigit():
                                            for digit in captcha_solution:
                                                await send_captcha_digits(url=interaction_post_url,
                                                                          session=session,
                                                                          session_id=session_id,
                                                                          message_id=message_id,
                                                                          digit=digit,
                                                                          data=post_data)
                                                await asyncio.sleep(random.uniform(0.3, 0.7))

                                            await solved.report_good(raise_exc=True)
                                            captcha_solved = True
                                            await websocket.close_connection()
                                            logger.info('🎉 Captcha verification completed successfully!')
                                            break
                                        else:
                                            await solved.report_bad(raise_exc=True)
                                            logger.error(
                                                '❌ Invalid captcha solution detected - initiating new solution request')

                    except KeyError:
                        continue


asyncio.run(main())
