from typing import Dict
import requests
from _config import RAPID_KEY, RAPID_HOST


def hotels_search(some_dict: Dict) -> Dict:
    result = dict()

    url = "https://hotels4.p.rapidapi.com/properties/list"
    headers = {
        'x-rapidapi-host': RAPID_HOST,
        'x-rapidapi-key': RAPID_KEY
    }

    sortOrder = "PRICE" if some_dict['cmd'] == 'lowprice' else "PRICE_HIGHEST_FIRST"

    querystring = {
        "destinationId": some_dict['destinationId'],
        "pageNumber": "1",
        "pageSize": "25",
        "checkIn": some_dict['checkIn'],
        "checkOut": some_dict['checkOut'],
        "adults1": "1",
        "sortOrder": sortOrder,
        "currency": some_dict['currency']
    }

    response = requests.request("GET", url, headers=headers, params=querystring).json()

    for elem in response['data']['body']['searchResults']['results']:
        result[elem['name']] = {
            'address': elem['address']['streetAddress'],
            'distance': elem['landmarks'][0]['distance'],
            'price': elem['ratePlan']['price']['fullyBundledPricePerStay'],
            'photo_url': elem['optimizedThumbUrls']['srpDesktop']
        }

    return result
