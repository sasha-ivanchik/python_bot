from typing import List
from datetime import datetime


def write_history(some_list: List, cmd_name: str, user_id: int) -> None:
    """
    Функция записи истории запросов и их результатов в файл
    :param some_list: список предложений-ответов от апи для записи
    :param cmd_name: название команды для записи
    :param user_id: id пользователя, чтобы при запросе истории не показывать лишнего
    """
    hotels_list = [hotel_name for elem in some_list for hotel_name in elem.keys()]
    hotels_str = ', '.join(hotels_list)
    cmd_time = datetime.now()

    with open('history.txt', 'a', encoding='utf-8') as file:
        our_string = f'{str(user_id)} :: {cmd_name} :: {cmd_time} :: {hotels_str}\n'
        file.write(our_string)


def read_history(user_id: int) -> List or bool:
    """
    Функция чтения истории запросов определённого пользователя
    :param user_id: id пользователя, чтобы при запросе истории показать только необходимое
    :return: список
    """
    result = []
    try:
        with open('history.txt', 'r', encoding='utf-8') as file:
            for line in file:
                if line.startswith(str(user_id)):
                    result.append(line.replace(str(user_id) + ' :: ', ""))
    except FileExistsError:
        return None
    else:
        return result
