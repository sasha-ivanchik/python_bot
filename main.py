import re
import telebot
from telebot import types
from _config import TG_TOKEN
from typing import List, Dict, Any
from datetime import datetime
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
from loguru import logger
from city_search import city_search
from hotels_search import hotels_search
from best_deal_search import best_deal_search
from history import write_history, read_history

# логирование
logger.add('log_file.log', format='{time}  ::  {level}  ::  {message}')

# имя бота SkillboxFinishWork ; ссылка t.me/SkillboxFinishWork_bot
bot = telebot.TeleBot(TG_TOKEN)

# набор реализованных команд
commands_list: List[str] = ['/start', '/help', '/lowprice', '/highprice',
                            '/bestdeal', '/history', '/hello_world']

# набор реализованных команд для всплывающей подсказки
cmd = [
    types.BotCommand('/start', 'Начало работы'),
    types.BotCommand('/help', 'Список всех доступных команд'),
    types.BotCommand('/hello_world', 'Тестовая команда'),
    types.BotCommand('/lowprice', 'Поиск самых недорогих предложений'),
    types.BotCommand('/highprice', 'Поиск самых дорогих предложений'),
    types.BotCommand('/bestdeal', 'Поиск лучших предложений по заданным параметрам'),
    types.BotCommand('/history', 'История запросов'),
]
bot.set_my_commands(commands=cmd)

# набор типов входящих сообщений, которые НЕ обрабатываются данным ботом
not_handling_messages: List[str] = ['audio', 'document', 'photo', 'sticker',
                                    'video', 'video_note', 'voice', 'location', 'contact',
                                    'new_chat_members', 'left_chat_member',
                                    'new_chat_title', 'new_chat_photo', 'delete_chat_photo',
                                    'group_chat_created', 'supergroup_chat_created',
                                    'channel_chat_created', 'migrate_to_chat_id',
                                    'migrate_from_chat_id', 'pinned_message']

# набор простых команд бота
simple_commands: Dict = {
    '/hello_world': lambda message: (bot.send_message(message.from_user.id, "hello world") and
                                     simple_commands['/help'](message)),
    'привет': lambda message: (bot.send_message(message.from_user.id, f'Привет, {message.from_user.first_name}!'
                                                                      f' Очень рады нашей встрече в ТГ!') and
                               simple_commands['greeting'](message)),
    '/help': lambda message: bot.send_message(message.from_user.id,
                                              '/start - начало работы бота\n'
                                              '/help - список всех доступных команд\n'
                                              '/hello_world - тестовая команда, выводит '
                                              'сообщение hello world\n'
                                              '/lowprice - поиск самых недорогих предложений\n'
                                              '/highprice - поиск самых дорогих предложений\n'
                                              '/bestdeal - поиск лучших предложений '
                                              'по заданным параметрам\n'
                                              '/history - история запросов'),
    'greeting': lambda message: bot.send_message(message.from_user.id,
                                                 '/start - начать поиск предложений. '
                                                 'Для получения списка всех '
                                                 'доступных команд введите команду /help. Так же'
                                                 'список всех команд доступен во всплывающем меню, '
                                                 'если вы введете слэш'
                                                 )
}

# список валют
currency_list: List[str] = ['USD', 'EUR', 'RUB']

# создаём календари для чекина и чекаута
calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1_callback = CallbackData("calendar_1", 'in', "action", "year", "month", "day")
calendar_2_callback = CallbackData("calendar_2", 'out', "action", "year", "month", "day")

# словарь необходимых для запроса данных
request_data = {
    'regular': {
        'city': '',
        'destinationId': '',
        'locale': '',
        'check_in': None,
        'check_out': None,
        'currency': None,
        'cmd': None,
        'quantity': 25,
    },
    'best_deal': {
        'money_min': None,
        'money_max': None,
        'distance_max': None,
    }
}

empty_data = {
    'regular': {
        'city': '',
        'destinationId': '',
        'locale': '',
        'check_in': None,
        'check_out': None,
        'currency': None,
        'cmd': None,
        'quantity': 25,
    },
    'best_deal': {
        'money_min': None,
        'money_max': None,
        'distance_max': None,
    }
}


def city_buttons(some_dict: Dict) -> Any:
    """
    Функция возвращает инлайн-клавиатуру с возможными вариантами городов для выбора необходимого
    :param some_dict - словарь с данными по городам
    """
    keyboard = None
    all_btns = []

    for elem in some_dict:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        call_text = elem + ', ' + some_dict[elem]['country']
        inline_btn = types.InlineKeyboardButton(text=call_text,
                                                callback_data=elem + ', ' + some_dict[elem]['id'] + '_city')
        all_btns.append(inline_btn)

    cancel_btn = types.InlineKeyboardButton(text='Отмена', callback_data='cancel_city')
    all_btns.append(cancel_btn)
    keyboard.add(*all_btns)

    return keyboard


def currency_buttons() -> Any:
    """
    Функция возвращает инлайн-клавиатуру с возможными вариантами валют
    """
    keyboard = None
    all_btns = []
    for elem in currency_list:
        keyboard = types.InlineKeyboardMarkup(row_width=len(currency_list))
        inline_btn = types.InlineKeyboardButton(text=elem, callback_data=elem + '_cur')
        all_btns.append(inline_btn)
    keyboard.add(*all_btns)

    return keyboard


def remove_keyboard(call: types.CallbackQuery) -> None:
    """
    Функция удаляет отображаемую инлайн клавиатуру
    """
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id)


def show_calendar(call: types.CallbackQuery) -> None:
    """
    Функция выводи инлайн-календарь для выбора даты заезда/выезда
    """
    now = datetime.now()
    if request_data['regular']['check_in'] is None:
        some_text = 'Выберите дату заезда'
        some_name = calendar_1_callback.prefix
    else:
        some_text = 'Выберите дату выезда'
        some_name = calendar_2_callback.prefix

    bot.send_message(call.from_user.id, text=some_text,
                     reply_markup=calendar.create_calendar(
                         name=some_name,
                         year=now.year,
                         month=now.month),
                     )


@logger.catch()
def get_quantity(msg: types.Message) -> None:
    """
    Функция получает максимальное число предложений, которое
    будет отправлено клиенту и запрашивает тип команды для поиска
    """
    if msg.text is None or msg.text.isdigit() is False:
        bot.send_message(msg.from_user.id, 'Будет выведено до 25 предложений')
    elif 0 < int(msg.text) <= 25:
        request_data['regular']['quantity'] = msg.text
        bot.send_message(msg.from_user.id, f'Будет выведено до {msg.text} предложений')
    else:
        bot.send_message(msg.from_user.id, 'Введите желаемое максимальное количество '
                                           'количество предложений для отображения еще раз (max 25)')
        bot.register_next_step_handler(msg, get_quantity)

    if request_data['regular']['cmd'] is None:
        simple_commands['/help'](msg)
    elif request_data['regular']['cmd'] in ('lowprice', 'highprice'):
        cmd_lowprice_highprice(msg)
    elif request_data['regular']['cmd'] == 'bestdeal':
        cmd_bestdeal(msg)


@logger.catch()
@bot.callback_query_handler(func=lambda xz: xz.data and xz.data.endswith('_cur'))
def choose_currency(call: types.CallbackQuery) -> None:
    currency = call.data[:-4]
    request_data['regular']['currency'] = currency
    bot.answer_callback_query(call.id,
                              f'Вы выбрали {currency} для отображения')
    remove_keyboard(call)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=f'Вы выбрали {currency} для отображения')

    bot.send_message(call.from_user.id, 'Введите желаемое максимальное количество '
                                        'количество предложений для отображения (max 25)')
    bot.register_next_step_handler(call.message, get_quantity)


@logger.catch()
@bot.callback_query_handler(func=lambda xz: xz.data and xz.data.endswith('_city'))
def choose_city(callback_query: types.CallbackQuery) -> None:
    code = callback_query.data[:-5].split(', ')
    if 'cancel' in code[0] or 'cancel' in code[1]:
        bot.answer_callback_query(callback_query.id, 'Отмена. Повторите ввод')
        remove_keyboard(callback_query)
        bot.edit_message_text(chat_id=callback_query.message.chat.id,
                              message_id=callback_query.message.message_id,
                              text='Начнём поиск города еще раз')
        cmd_start(callback_query)

    else:
        request_data['regular']['city'] = code[0]
        request_data['regular']['destinationId'] = code[1]
        bot.answer_callback_query(callback_query.id,
                                  f'Поиск отелей будет производится в городе {code}')
        # удаляем клавиатуру
        remove_keyboard(callback_query)
        # редактируем сообщение
        bot.edit_message_text(chat_id=callback_query.message.chat.id,
                              message_id=callback_query.message.message_id,
                              text=f'Поиск предложений будет производится в : {code[0]}')

        show_calendar(callback_query)


@logger.catch()
@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1_callback.prefix))
def choose_date_in(call: types.CallbackQuery) -> None:
    """
    Функция обработки callback запросов для даты заезда в отель
    """
    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day)

    if action == "DAY":
        if date.strftime('%Y-%m-%d') > datetime.now().strftime('%Y-%m-%d'):
            request_data['regular']['check_in'] = date.strftime('%Y-%m-%d')
            some_text = 'Дата заезда  :  ' + request_data['regular']['check_in']

            bot.send_message(
                chat_id=call.from_user.id,
                text=some_text,
                reply_markup=types.ReplyKeyboardRemove(),
            )
            show_calendar(call)
        else:
            some_text = 'Дата заезда не может быть раньше текущей даты.'
            bot.send_message(
                chat_id=call.from_user.id,
                text=some_text)
            show_calendar(call)

    elif action == "CANCEL":
        bot.send_message(
            chat_id=call.from_user.id,
            text="Выбор даты отменён. Необходимо начать сначала",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        cmd_start(call)


@logger.catch()
@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_2_callback.prefix))
def choose_date_out(call: types.CallbackQuery) -> None:
    """
    Функция обработки callback запросов для даты выезда из отеля
    """
    name, action, year, month, day = call.data.split(calendar_2_callback.sep)
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day)

    if action == "DAY":
        if date.strftime('%Y-%m-%d') > request_data['regular']['check_in']:
            request_data['regular']['check_out'] = date.strftime('%Y-%m-%d')
            some_text = 'Дата выезда  :  ' + request_data['regular']['check_out']

            bot.send_message(
                chat_id=call.from_user.id,
                text=some_text,
                reply_markup=types.ReplyKeyboardRemove(),
            )
            keyboard = currency_buttons()
            bot.send_message(
                chat_id=call.from_user.id,
                text='Выберите подходящую для вас валюту',
                reply_markup=keyboard
            )

        else:
            some_text = 'Дата выезда не может быть раньше даты заезда.'
            bot.send_message(
                chat_id=call.from_user.id,
                text=some_text)
            show_calendar(call)

    elif action == "CANCEL":
        bot.send_message(
            chat_id=call.from_user.id,
            text="Выбор даты отменён. Необходимо начать сначала",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        cmd_start(call)


@logger.catch()
def get_city(message: types.Message) -> None:
    """
    Функция проверки названия города и поиска его данных на Hotels.com через импортированную функцию city_search.
    Выводит клавиатуру с найденными вариантами городов и стран
    """
    if message.text and all(sym.isalpha() for sym in message.text):
        bot.send_message(message.from_user.id, 'Идёт обработка запроса')
        location_data, request_data['regular']['locale'] = city_search(message.text)
        # вывод найденных вариантов
        if location_data and location_data != 'timeout':
            keyboard = city_buttons(location_data)
            bot.send_message(message.from_user.id, 'Возможные варианты', reply_markup=keyboard)
        elif location_data and location_data == 'timeout':
            bot.send_message(message.from_user.id, 'Сервер долго не отвечает. Попробуйте еще раз')
            cmd_start(message)
        else:
            bot.send_message(message.from_user.id, 'Не удалось найти город по вашему запросу')
            cmd_start(message)
    else:
        bot.send_message(message.from_user.id, 'Обнаружена ошибка в названии города')
        cmd_start(message)


@logger.catch()
@bot.message_handler(commands=['start'])
def cmd_start(message: types.Message or types.CallbackQuery) -> None:
    """
    Функция команды /start
    """
    bot.send_message(message.from_user.id, 'Введите название города,'
                                           'в котором вы хотели бы остановиться')
    if isinstance(message, types.CallbackQuery):
        bot.register_next_step_handler(message.message, get_city)
    else:
        bot.register_next_step_handler(message, get_city)


@logger.catch()
@bot.message_handler(commands=['history'])
def cmd_history(msg: types.Message) -> None:
    """
    Функция команды history
    :param msg: сообщение от пользователя
    :return: ответное сообщение с историей запросов данного пользователя
    """
    history_listing = read_history(user_id=msg.from_user.id)
    if history_listing:
        counter = 1
        for story in history_listing:
            bot.send_message(msg.from_user.id, str(counter) + ') ' + story)
            counter += 1
        simple_commands['/help'](msg)
    else:
        bot.send_message(msg.from_user.id, "Вы не совершали действий, которые были бы записаны в историю")
        simple_commands['/help'](msg)


@logger.catch()
def sending_results(msg: types.Message, some_list: List[Dict]) -> None:
    """
    Функция отправляет все найденные предложения пользователю в ТГ
    :param msg: сообщение пользователя
    :param some_list: список словарей результатов для отправки в сообщения
    :return: ничего
    """
    global request_data
    for elem in some_list:
        for key, value in elem.items():
            if value["photo_url"]:
                photo = value["photo_url"]
            else:
                photo = "https://vestikavkaza.ru/upload/2018-04-13/15236090055ad06dad2003b3.53059342.png"
            text = (f'*Отель*  :\n{key}\n\n'
                    f'*Адрес отеля*  :\n{value["address"]}\n\n'
                    f'*Расстояние до центра города*  :\n{value["distance"]}\n\n'
                    f'*Стоимость всего проживания*  :\n{value["price"]}\n\n'
                    f'*Ссылка для бронирования*  :\n{value["url"]}')
            bot.send_photo(msg.chat.id, photo, caption=text, parse_mode="Markdown")

    write_history(some_list=some_list, cmd_name=request_data['regular']['cmd'], user_id=msg.from_user.id)

    request_data = empty_data
    simple_commands['/help'](msg)


@logger.catch()
@bot.message_handler(commands=['lowprice', 'highprice'])
def cmd_lowprice_highprice(message: types.Message) -> None:
    """
    Функция команд /lowprice ,  /highprice
    :param message: сообщение-вызов от пользователя
    """
    global request_data
    global empty_data

    if message.text[1:] in ('lowprice', 'highprice'):
        request_data['regular']['cmd'] = 'lowprice' if message.text[1:] == 'lowprice' else 'highprice'

    if all(request_data['regular'].values()):
        bot.send_message(message.chat.id, 'Идёт обработка запроса')
        answer = hotels_search(request_data['regular'])
        if answer and answer != 'timeout':
            sending_results(message, answer)
            request_data = empty_data
        elif answer == 'timeout':
            bot.send_message(message.from_user.id, "Сервер долго не отвечает. Попробуйте еще раз")
            request_data = empty_data
            cmd_start(message)
        else:
            bot.send_message(message.from_user.id,
                             "К сожалению, не удалось найти подходящие вам предложения. Попробуйте ещё раз")
            request_data = empty_data
            cmd_start(message)

    else:
        if request_data['regular']['city'] == '':
            cmd_start(message)


@logger.catch()
def get_distance(msg: types.Message) -> None:
    """
    Функция-запрос максимального расстояния до центра города
    :param msg: сообщение от пользователя
    """
    if msg.text:
        pre_distance = re.sub(r'[,]', '.', msg.text)
        max_distance = re.findall(r'^[0-9]*[.]?[0-9]+$', pre_distance)
        if len(max_distance) == 1:
            request_data['best_deal']['distance_max'] = max_distance[0]
            bot.send_message(msg.from_user.id,
                             f"Максимальное удаление от центра : {request_data['best_deal']['distance_max']}")
        else:
            bot.send_message(msg.from_user.id,
                             f"Введите 1!(одно) число. Возможен ввод числа с дробной частью")
            bot.register_next_step_handler(msg, get_distance)
    else:
        bot.send_message(msg.from_user.id, 'Введите 1!(одно) число. Возможен ввод числа с дробной частью')
        bot.register_next_step_handler(msg, get_distance)

    cmd_bestdeal(msg)


@logger.catch()
def get_money(msg: types.Message) -> None:
    """
    Функция-запрос диапазона подходязщих цен и его проверка
    :param msg: сообщение от пользователя
    """
    if msg.text:
        money_range = re.findall(r'\d+', msg.text)
        if len(money_range) == 2:
            request_data['best_deal']['money_min'] = min(money_range)
            request_data['best_deal']['money_max'] = max(money_range)
            bot.send_message(msg.from_user.id,
                             f"Минимальная стоимость от : {request_data['best_deal']['money_min']}\n"
                             f"Максимальная стоимость до : {request_data['best_deal']['money_max']}")
        else:
            bot.send_message(msg.from_user.id,
                             f"Введите 2!(два) отделённых друг от друга числа")
            bot.register_next_step_handler(msg, get_money)
    else:
        bot.send_message(msg.from_user.id, 'Введите 2!(два) отделённых друг от друга числа')
        bot.register_next_step_handler(msg, get_money)
    bot.send_message(msg.from_user.id, "Укажите максимальное удаление от центра города. "
                                       "Возможен ввод числа с дробной частью")
    bot.register_next_step_handler(msg, get_distance)


@logger.catch()
@bot.message_handler(commands=['bestdeal'])
def cmd_bestdeal(msg: types.Message) -> None:
    """
    Функция для команды bestdeal
    :param msg: сообщение-вызов от пользователя
    """
    global request_data
    global empty_data

    request_data['regular']['cmd'] = 'bestdeal'
    if request_data['regular']['city']:
        if request_data['best_deal']['distance_max']:
            bot.send_message(msg.chat.id, 'Идёт обработка запроса')
            answer = best_deal_search(request_data)
            if answer:
                sending_results(msg, answer)
                request_data = empty_data
            else:
                bot.send_message(msg.from_user.id,
                                 "К сожалению, не удалось найти подходящие вам предложения. Попробуйте ещё раз")
                request_data = empty_data
                simple_commands['/help'](msg)
        else:
            bot.send_message(msg.chat.id,
                             f'Введите подходящий диапазон цен (2 числа!) '
                             f'в {request_data["regular"]["currency"]}')
            bot.register_next_step_handler(msg, get_money)
    else:
        if request_data['regular']['city'] == '':
            cmd_start(msg)


@logger.catch()
@bot.message_handler(content_types=['text'])
def text_handler(message: types.Message) -> None:
    """
    Функция-обработчик текстовых сообщений.
    """
    if message.text.lower() in simple_commands and message.text.lower() != 'greeting':
        simple_commands[message.text.lower()](message)

    elif message.text.lower().startswith('/') is False \
            and message.text.lower() not in ('привет', 'greeting'):
        bot.send_message(message.from_user.id, "Привет " + message.from_user.first_name + '! Меньше слов больше дела!')
        simple_commands['greeting'](message)

    elif message.text.lower().startswith('/') and \
            message.text.lower() not in commands_list:
        bot.send_message(message.from_user.id, 'Команда введена некорректно.')
        simple_commands['greeting'](message)


@bot.message_handler(content_types=not_handling_messages)
def get_unhandling_msg(message: types.Message) -> None:
    """
    Функция обработчик сообщений неподдерживаемых типов.
    :param message: сообщение любого типа, который не поддерживается данным ботом
    """
    bot.send_message(message.from_user.id,
                     'К сожалению, данный тип сообщение я не могу обработать :(\n'
                     'Для начала работы необходимо ввести '
                     'команду "/start". Для получения списка всех'
                     'доступных команд введите команду "/help"')


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=10)
        except Exception as error:
            logger.exception(str(error))
