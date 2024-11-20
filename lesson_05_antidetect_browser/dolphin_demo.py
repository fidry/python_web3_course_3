import requests

import config


profile_id = '488330839'
open_profile_url = f'{config.DOLPHIN_API_URI}/v1.0/browser_profiles/{profile_id}/start?automation=1'
profile_data = requests.get(open_profile_url).json()
print(profile_data)
'''
    {
        'success': True, 
        'automation': {
            'port': 50266, 
            'wsEndpoint': '/devtools/browser/7bd6cae8-2a16-476d-be67-0a72fcef62f0'
        }
    }
'''
