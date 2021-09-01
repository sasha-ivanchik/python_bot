import requests
import re
from typing import Dict
from _config import RAPID_KEY, RAPID_HOST


def city_search(some_str: str) -> Dict:
    result = dict()

    url = "https://hotels4.p.rapidapi.com/locations/search"
    headers = {
        'x-rapidapi-host': RAPID_HOST,
        'x-rapidapi-key': RAPID_KEY
    }

    city = some_str.lower().capitalize()
    locale = 'ru_RU' if re.match(r'[А-Яа-яЁё]+', city) else 'en_US'

    querystring = {"query": city, "locale": locale}
    response = requests.request("GET", url, headers=headers, params=querystring).json()

    for elem in response['suggestions'][0]['entities']:
        result[elem['name']] = elem["destinationId"]

    return result
