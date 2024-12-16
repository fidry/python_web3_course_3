# from fake_useragent import FakeUserAgent

from my_keys import token_15

target_channel_id = "1197089363742425099"  # Замените на ID нужного канала
pandez_bot_id = "967155551211491438"  # Замените на ID бота, от которого хотите получать сообщения

interaction_post_url = 'https://discord.com/api/v9/interactions'

uri = "wss://gateway.discord.gg/?v=10&encoding=json"

# user_agent = FakeUserAgent(browsers='chrome', os='macos').random

headers_interaction = {
    'authority': 'discord.com',
    'accept': '*/*',
    'accept-language': 'ru',
    'authorization': token_15,
    'content-type': 'application/json',
    'origin': 'https://discord.com',
    'referer': 'https://discord.com/channels/930828907194749019/1197089363742425099',
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, "
                  "like Gecko) Chrome/122.0.0.0 Safari/537.36",
    'x-debug-options': 'bugReporterEnabled',
    'x-discord-locale': 'ru',
    'x-discord-timezone': 'Europe/Berlin',
    'x-super-properties': 'eyJvcyI6Ik1hYyBPUyBYIiwiYnJvd3NlciI6IkNocm9tZSIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJydSI'
                          'sImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChNYWNpbnRvc2g7IEludGVsIE1hYyBPUyBYIDEwXzE1Xzc'
                          'pIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS8xMjIuMC4wLjAgU2FmYXJpLzUzNy4'
                          'zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjEyMi4wLjAuMCIsIm9zX3ZlcnNpb24iOiIxMC4xNS43IiwicmVmZXJyZXIiOiJ'
                          'odHRwczovL3d3dy5nb29nbGUuY29tLyIsInJlZmVycmluZ19kb21haW4iOiJ3d3cuZ29vZ2xlLmNvbSIsInNlYXJjaF'
                          '9lbmdpbmUiOiJnb29nbGUiLCJyZWZlcnJlcl9jdXJyZW50IjoiaHR0cHM6Ly9wb2ludHMucmVkZGlvLmNvbS8iLCJy'
                          'ZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiJwb2ludHMucmVkZGlvLmNvbSIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJs'
                          'ZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjMzOTIyMSwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=',
}

post_data = {
    'type': 3,
    'nonce': None,
    'guild_id': '930828907194749019',
    'channel_id': '1197089363742425099',
    'message_flags': 0,
    'message_id': '1197089366342909993',
    'application_id': pandez_bot_id,
    'session_id': None,
    'data': {
        'component_type': 2,
        'custom_id': None,
    },
}

# payload = {'op': 2, 'd': {'token': f'{token_12}', 'properties': {'$os': 'Mac OS X', '$browser': 'Chrome'}}}

payload = {
    "op": 2,
    "d": {
        "token": token_15,
        "capabilities": 30717,
        "properties": {
            "os": "Mac OS X",
            "browser": "Chrome",
            "device": "",
            "system_locale": "ru",
            "browser_user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, "
                                  "like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "browser_version": "122.0.0.0",
            "os_version": "10.15.7",
            "referrer": "",
            "referring_domain": "",
            "referrer_current": "https://points.reddio.com/",
            "referring_domain_current": "points.reddio.com",
            "release_channel": "stable",
            "client_build_number": 347699,
            "client_event_source": None
        },
        "presence": {
            "status": "unknown",
            "since": 0,
            "activities": [],
            "afk": False
        },
        "compress": False,
        "client_state": {
            "guild_versions": {}
        }
    }
}
