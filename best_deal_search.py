from typing import Dict, List
import re
from hotels_search import hotels_search
from hotels_search import foo_for_sort


def filtration(list_for_filtration: List, custom_distance: str) -> List:
    """
    Функция фильтрации полученных от апи предложений по расстоянию до центра города
    :param list_for_filtration : список полученных словарей-предложений
    :param custom_distance : строка из запроса, содержит введенное пользователем значение расстояния
    :return: список словарей-предложений, которые подходят по заданному расстоянию
    """
    filtered_res = []
    for k_elem in list_for_filtration:
        for k_key, k_value in k_elem.items():
            if clear_distance(k_value) <= float(custom_distance):
                filtered_res.append(k_elem)

    return filtered_res


def clear_distance(dict_for_extract: Dict) -> float:
    """
    Функция обработки одного словаря-результата, которая извлекает,
    обрабатывает и возвращает значение дистанции до центра города
    :param dict_for_extract: словарь данных конкретного отеля
    :return: float значение расстояния от отеля до центра города
    """
    pre_distance_frst = re.sub(r'[,]', '.', dict_for_extract['distance'])
    our_distance_frst = re.findall(r'\b[0-9]*[.]?[0-9]+\b', pre_distance_frst)[0]
    return float(our_distance_frst)


def best_deal_search(some_dict: Dict, ) -> List:
    """
    Функция кастомного поиска топ недорогих предложений с учетом максимальной
     и минимальной стоимости и удаленности от центра через API сайта hotels.com
    :param some_dict: словарь с данными для запроса
        some_dict = {
            'regular': {
                'city': '', # город, в котором будет производится поиск
                'destinationId': '', # id города в API сайта
                'locale': '', # наименование базы данных по языку
                'check_in': , # дата заезда
                'check_out': , # дата выезда
                'currency': , # валюта
                'cmd': , # наименование команды для определения метода сортировки
                'quantity': , # максимальное количество запрашиваемых предложений
            },
            'best_deal': {
                'money_min':  # минимальная стоимость
                'money_max': # максимальная стоимость
                'distance_max': # максимальное расстояние до центра,
            }
        }
    :return: словарь с результатами поиска
        result = {
            'name' : {  #  название отеля
                'address': '', # адрес отеля
                'distance': '', # расстояние до центра
                'photo_url': '', # ссылка на фото
                'url': , # ссылка на отель в hotels.com
                'price': , # полная стоимость проживания
            }
        }
    """
    money_min = some_dict['best_deal']['money_min']
    money_max = some_dict['best_deal']['money_max']
    page_counter = 1
    max_distance = some_dict['best_deal']['distance_max']
    total_offers = some_dict['regular']['quantity']

    # запрос к апи с параметрами
    pre_result = hotels_search(some_dict=some_dict['regular'],
                               page=page_counter,
                               money_min=money_min,
                               money_max=money_max,
                               )
    # первая фильтрация данных от апи
    result = filtration(pre_result, max_distance)

    # дополняем словарь результатами поиска, если при первом запросе результатов мало
    while len(result) < int(total_offers):
        page_counter += 1
        additional_result = hotels_search(some_dict=some_dict['regular'],
                                          page=page_counter,
                                          money_min=money_min,
                                          money_max=money_max,
                                          )
        # фильтрация данных и добавление подходящих в список результатов
        result.extend(filtration(additional_result, max_distance))

        # ограничение по количеству пролистываний
        if page_counter > 3:
            break

    # сортировка полученного списка по стоимости по возрастанию
    ready_list = foo_for_sort(result, False)

    # обрезаем лишние результаты , если результатов больше , чем нужно
    if len(ready_list) > int(total_offers):
        return ready_list[:int(total_offers)]

    return ready_list
