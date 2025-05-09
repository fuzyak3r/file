import re
import json
import time
import requests
from urllib.parse import urlencode

# Steam OpenID configuration
STEAM_OPENID_URL = 'https://steamcommunity.com/openid/login'
STEAM_API_KEY = ''  # You'll need to get an API key from https://steamcommunity.com/dev/apikey

def generate_steam_login_url(return_url):
    """
    Generate Steam OpenID login URL
    """
    params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': return_url,
        'openid.realm': return_url.rsplit('/', 1)[0],
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select'
    }
    
    return f"{STEAM_OPENID_URL}?{urlencode(params)}"

def validate_steam_login(params):
    """
    Validate the Steam login response
    """
    # Verify the signature by making another request to Steam
    params['openid.mode'] = 'check_authentication'
    response = requests.post(STEAM_OPENID_URL, data=params)
    
    if 'is_valid:true' in response.text:
        # Extract the Steam ID from the claimed_id
        match = re.search(r'(https?://steamcommunity.com/openid/id/)?(\d+)', params.get('openid.claimed_id', ''))
        if match:
            return match.group(2)  # Return the Steam ID
    
    return None

def get_steam_user_info(steam_id):
    """
    Get user info from Steam API
    """
    if not STEAM_API_KEY:
        # If no API key, return minimal info
        return {
            'steamid': steam_id,
            'personaname': f'User_{steam_id[-5:]}',
            'avatar': '',
            'profileurl': f'https://steamcommunity.com/profiles/{steam_id}/'
        }
    
    # Make request to Steam API
    response = requests.get(
        'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/',
        params={
            'key': STEAM_API_KEY,
            'steamids': steam_id
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        if data and 'response' in data and 'players' in data['response'] and data['response']['players']:
            return data['response']['players'][0]
    
    # If API request fails or no API key, return minimal info
    return {
        'steamid': steam_id,
        'personaname': f'User_{steam_id[-5:]}',
        'avatar': '',
        'profileurl': f'https://steamcommunity.com/profiles/{steam_id}/'
    }