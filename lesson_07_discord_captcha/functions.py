import asyncio
from datetime import datetime

from loguru import logger
from requests import Session


def time_snowflake(dt: datetime, /, *, high: bool = False) -> int:
    discord_millis = int(dt.timestamp() * 1000 - 1420070400000)
    return (discord_millis << 22) + (2 ** 22 - 1 if high else 0)


async def press_buttons(url: str, session: Session, session_id: str, custom_id: str, data: dict, message_id: str = None):
    # if message_id:
    #     data['nonce'] = time_snowflake(datetime.utcnow())
    #     data['message_flags'] = 64
    #     data['message_id'] = message_id
    #     data['session_id'] = session_id
    #     data['data']['custom_id'] = custom_id
    # else:
    #     data['nonce'] = time_snowflake(datetime.utcnow())
    #     data['session_id'] = session_id
    #     data['data']['custom_id'] = custom_id

    data['nonce'] = time_snowflake(datetime.utcnow())
    data['session_id'] = session_id
    data['data']['custom_id'] = custom_id

    if message_id:
        data['message_flags'] = 64
        data['message_id'] = message_id

    press_button = session.post(url=url,
                                json=data)
    logger.debug(f"📎 Request payload: {data}")

    if message_id:
        logger.info(f'⚡ Button pressed: "{custom_id}" | status: {press_button.status_code}')
    else:
        logger.info(f'⚡ Button pressed: "{custom_id}" | status: {press_button.status_code}')
    await asyncio.sleep(2)


async def send_captcha_digits(url: str, session: Session, session_id: str, message_id: str, digit: str, data: dict):
    data['nonce'] = time_snowflake(datetime.utcnow())
    data['message_flags'] = 64
    data['message_id'] = message_id
    data['session_id'] = session_id
    data['data']['custom_id'] = digit

    send_digit = session.post(url=url,
                              json=data)

    logger.debug(f'🔢 Sent digit: {digit} | status: {send_digit.status_code}')
    await asyncio.sleep(2)


# async def get_message(session: Session) -> str:
#     response = session.get('https://discord.com/api/v9/channels/1197089363742425099/messages?limit=50')
#     data = response.json()
#     data_json = data[0]
#     message = data_json['embeds'][0]['description']
#     return message

