import requests
import re
from typing import Dict
from _config import RAPID_KEY, RAPID_HOST


def city_search(some_str: str) -> Dict and str:
    """
    функция поиска города по названию
    :param some_str: сообщение от пользователя
    :return:  1)словарь( ключ - название города, значение -
    кортеж  (названия страны, id)
                2)строка-указатель базы, в которой искали город
    """
    result = dict()

    url = "https://hotels4.p.rapidapi.com/locations/search"
    headers = {
        'x-rapidapi-host': RAPID_HOST,
        'x-rapidapi-key': RAPID_KEY
    }
    # проверка определяет язык, на котором пользователь ввёл название города
    city = some_str.lower().capitalize()
    locale = 'ru_RU' if re.match(r'[А-Яа-яЁё]+', city) else 'en_US'

    querystring = {"query": city, "locale": locale}

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)
    except requests.Timeout:
        return 'timeout', locale

    if response.status_code == 200:
        try:
            for elem in response.json()['suggestions'][0]['entities']:
                result[elem['name']] = dict()

                # получение названия страны из строки с тегами
                some_text = elem['caption'].split(', ')[-1]
                country_name = re.sub(r'<[^>]*>','', some_text)

                result[elem['name']]['country'] = country_name
                result[elem['name']]['id'] = elem["destinationId"]
        except Exception:
            raise Warning('К сожалению, технические неполадки')
    else:
        raise Warning('К сожалению, технические неполадки')

    return result, locale
