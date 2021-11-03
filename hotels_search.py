from typing import List, Dict, Any
import requests
import re
from _config import RAPID_KEY, RAPID_HOST
from datetime import datetime


def accommodation(date_in: str, date_out: str) -> int:
    """
    Функция для расчета время проживания
    :param date_in: дата заезда
    :param date_out: дата выезда
    :return: количество ночей в отеле
    """
    ch_in = datetime.strptime(date_in, '%Y-%m-%d')
    ch_out = datetime.strptime(date_out, '%Y-%m-%d')
    total_nights = (ch_out - ch_in).days
    return total_nights


def foo_for_sort(some_list: List, sort_direction: bool) -> List:
    """Функция сортировки списка словарей результатов по параметру price_in_numbers
     :param some_list - список словарей результатов поиска
     :param sort_direction - направоение сортировки, реверс  если True
     :return отсортированный список словарей результатов поиска
     """

    def custom_sort(xz_dict: Dict) -> Any:
        """
        функция для сортировки списка словарей
        :param xz_dict: произвольный список словарей
        :return: значение поля price_in_numbers из словаря
        """
        for k, v in xz_dict.items():
            if v['price_in_numbers']:
                return v['price_in_numbers']

    ready_list = sorted(some_list, key=custom_sort, reverse=sort_direction)
    return ready_list


def hotels_search(some_dict: Dict,
                  page: int = 1,
                  money_min: int = None,
                  money_max: int = None,
                  ) -> List or bool:
    """
    Функция поиска топ дорогих или топ дешевых предложений через API сайта hotels.com по заданным параметрам
    :param some_dict: словарь с данными для запроса
        some_dict = {
            'city': '', # город, в котором будет производится поиск
            'destinationId': '', # id города в API сайта
            'locale': '', # наименование базы данных по языку
            'check_in': , # дата заезда
            'check_out': , # дата выезда
            'currency': , # валюта
            'cmd': , # наименование команды для определения метода сортировки
            'quantity': , # максимальное количество запрашиваемых предложений
        }
    :param page: int - номер страницы вывода результатов в апи. по умолчанию = 1
    :param money_min - минимальная стоимость. по умолчанию None
    :param money_max - максимальная стоимость. по умолчанию None

    :return: список словарей с результатами поиска
        result = [
            'name' : {  #  название отеля
                'address': '', # адрес отеля
                'distance': '', # расстояние до центра
                'photo_url': '', # ссылка на фото
                'url': , # ссылка на отель в hotels.com
                'price': , # полная стоимость проживания
                'price_in_numbers':  # полная стоимость в виде целого числа для сортировки
            },
            ...
        ]
    """

    result = dict()

    url = "https://hotels4.p.rapidapi.com/properties/list"
    headers = {
        'x-rapidapi-host': RAPID_HOST,
        'x-rapidapi-key': RAPID_KEY
    }

    sort_order = "PRICE" if some_dict['cmd'] in ('lowprice', 'bestdeal') else "PRICE_HIGHEST_FIRST"
    page_size = str(some_dict['quantity']) if some_dict['cmd'] in ('lowprice', 'highprice') else '25'

    querystring = {
        "destinationId": some_dict['destinationId'],
        "pageNumber": page,
        "pageSize": page_size,
        "checkIn": some_dict['check_in'],
        "checkOut": some_dict['check_out'],
        "adults1": 1,
        "sortOrder": sort_order,
        "currency": some_dict['currency'],
        "locale": some_dict['locale'],
        "priceMin": money_min,
        "priceMax": money_max,
    }

    try:
        main_response = requests.request("GET", url, headers=headers, params=querystring, timeout=15)
    except requests.Timeout:
        return "timeout"

    try:
        response = main_response.json()
    except Exception:
        return "timeout"

    if main_response.status_code == 200 and response['result'] == 'OK':

        for elem in response['data']['body']['searchResults']['results']:
            result[elem['name']] = {
                'distance': elem['landmarks'][0]['distance'],
                'photo_url': elem['optimizedThumbUrls']['srpDesktop'],
                'url': "https://www.hotels.com/ho" + str(elem['id']),
            }

            # проверка наличия полной стоимости проживания и расчёт при её отсутствии
            nights = accommodation(some_dict['check_in'], some_dict['check_out'])
            if 'fullyBundledPricePerStay' in elem['ratePlan']['price']:
                field_nums_list = re.findall(r"(?<![a-zA-Z:])[-+]?\d*[.,]?\d+",
                                             elem['ratePlan']['price']['fullyBundledPricePerStay'])
                result[elem['name']]['price'] = (f"{field_nums_list[0]} {some_dict['currency']} "
                                                 f"за {field_nums_list[1]} суток")
                price_for_compare = re.sub(r'[.,]', '', field_nums_list[0])
                result[elem['name']]['price_in_numbers'] = int(price_for_compare)

            else:
                result[elem['name']]['price'] = (re.sub(r"[^0-9]", "", elem["ratePlan"]["price"]["current"]) +
                                                 ' ' + some_dict["currency"] + ' за ' + str(nights) + ' суток')
                result[elem['name']]['price_in_numbers'] = int(
                    re.sub(r"[^0-9]", "", elem["ratePlan"]["price"]["current"]))

            # проверка на наличие поля с адресом и возврат текста-заглушки при отсутствии таковой
            address = elem['address']['streetAddress'] \
                if 'streetAddress' in elem['address'] else "Данные об адресе отсутствуют"
            result[elem['name']]['address'] = address

    else:
        return "timeout"

    # преобразуем словарь словарей в список чтобы отсортировать
    result_list = [{elem: result[elem]} for elem in result]
    desc_flag = False if sort_order == "PRICE" else True
    ready_list = foo_for_sort(result_list, desc_flag)

    return ready_list
