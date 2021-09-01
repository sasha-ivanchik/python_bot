import telebot
from telebot import types
from city_search import city_search
from hotels_search import hotels_search
from _config import TG_TOKEN
import typing
from datetime import datetime
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE

bot = telebot.TeleBot(TG_TOKEN)
# имя бота SkillboxFinishWork ; ссылка t.me/SkillboxFinishWork_bot

# набор реализованных команд
commands_list: typing.List[str] = ['/start', '/help', '/lowprice', '/highprice',
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
not_handling_messages: typing.List[str] = ['audio', 'document', 'photo', 'sticker',
                                           'video', 'video_note', 'voice', 'location', 'contact',
                                           'new_chat_members', 'left_chat_member',
                                           'new_chat_title', 'new_chat_photo', 'delete_chat_photo',
                                           'group_chat_created', 'supergroup_chat_created',
                                           'channel_chat_created', 'migrate_to_chat_id',
                                           'migrate_from_chat_id', 'pinned_message']

# набор простых команд бота
simple_commands: typing.Dict = {
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
currency_list: typing.List[str] = ['USD', 'EUR', 'RUB']

# создаём календари для чекина и чекаута
calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1_callback = CallbackData("calendar_1", 'in', "action", "year", "month", "day")
calendar_2_callback = CallbackData("calendar_2", 'out', "action", "year", "month", "day")

# словарь необходимых для запроса данных
request_data = {
    'city': '',
    'destinationId': '',
    'checkIn': None,
    'checkOut': None,
    'currency': None,
    'cmd': None,
}

# флаг для доп сообщения при первом старте
first_start_flag = True

# словарь возможных городов
location_data = dict()


def city_buttons(some_list: typing.List) -> typing.Any:
    """
    Функция возвращает инлайн-клавиатуру с
    возможными вариантами городов для выбора необходимого города
    """
    keyboard = None
    all_btns = []

    for elem in some_list:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        inline_btn = types.InlineKeyboardButton(text=elem, callback_data=elem + '_city')
        all_btns.append(inline_btn)

    cancel_btn = types.InlineKeyboardButton(text='Отмена', callback_data='cancel_city')
    all_btns.append(cancel_btn)

    keyboard.add(*all_btns)

    return keyboard


def currency_buttons() -> typing.Any:
    """
    Функция возвращает инлайн-клавиатуру с
    возможными вариантами валют
    """
    global currency_list

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
    Функция выводи календарь для выбора даты заезда/выезда
    """
    now = datetime.now()
    if request_data['checkIn'] is None:
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


@bot.callback_query_handler(func=lambda xz: xz.data and xz.data.endswith('_cur'))
def choose_currency(call: types.CallbackQuery) -> None:
    currency = call.data[:-4]
    request_data['currency'] = currency
    bot.answer_callback_query(call.id,
                              f'Вы выбрали {currency} для отображения')
    # удаляем клавиатуру
    remove_keyboard(call)

    # редактируем сообщение
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=f'Вы выбрали {currency} для отображения')
    if request_data['cmd'] is None:
        bot.send_message(call.from_user.id,
                         'Введите команду для дальнейшей работы:\n'
                         '/lowprice - поиск самых недорогих предложений\n'
                         '/highprice - поиск самых дорогих предложений\n'
                         '/bestdeal - поиск лучших предложений '
                         'по заданным параметрам\n'
                         '/history - история запросов')
    elif request_data['cmd'] == 'lowprice':
        cmd_lowprice_highprice(call.message)


@bot.callback_query_handler(func=lambda xz: xz.data and xz.data.endswith('_city'))
def choose_city(callback_query: types.CallbackQuery) -> None:
    global request_data
    global location_data

    code = callback_query.data[:-5]
    if code.startswith('cancel'):
        bot.answer_callback_query(callback_query.id, 'Отмена. Повторите ввод')

        # удаляем клавиатуру
        remove_keyboard(callback_query)

        # редактируем сообщение
        bot.edit_message_text(chat_id=callback_query.message.chat.id,
                              message_id=callback_query.message.message_id,
                              text='Начнём поиск города еще раз')

        cmd_start(callback_query)

    else:
        request_data['city'] = code
        request_data['destinationId'] = location_data[code]
        bot.answer_callback_query(callback_query.id,
                                  f'Поиск отелей будет производится в городе {code}')

        # удаляем клавиатуру
        remove_keyboard(callback_query)

        # редактируем сообщение
        bot.edit_message_text(chat_id=callback_query.message.chat.id,
                              message_id=callback_query.message.message_id,
                              text=f'Поиск предложений будет производится в : {code}')

        show_calendar(callback_query)


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1_callback.prefix))
def choose_date_in(call: types.CallbackQuery) -> None:
    """
    Функция обработки callback запросов для даты заезда
    """
    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day)

    if action == "DAY":
        if date.strftime('%Y-%m-%d') > datetime.now().strftime('%Y-%m-%d'):
            request_data['checkIn'] = date.strftime('%Y-%m-%d')
            some_text = request_data['city'] + ' --in-- ' + request_data['checkIn']

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


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_2_callback.prefix))
def choose_date_out(call: types.CallbackQuery) -> None:
    """
    Функция обработки callback запросов для даты заезда
    """
    name, action, year, month, day = call.data.split(calendar_2_callback.sep)
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day)

    if action == "DAY":
        if date.strftime('%Y-%m-%d') > request_data['checkIn']:
            request_data['checkOut'] = date.strftime('%Y-%m-%d')
            some_text = request_data['city'] + ' --out-- ' + request_data['checkOut']

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


def get_city(message: types.Message) -> None:
    """
    Функция проверки названия города и поиска его данных на Hotels.com
    через импортированную функцию city_search.
    Выводит клавиатуру с найденными вариантами городов
    """
    global location_data

    if message.text and all(sym.isalpha() for sym in message.text):
        bot.send_message(message.from_user.id, 'Идёт обработка запроса')
        location_data = city_search(message.text)

        # вывод найденных вариантов
        if location_data:
            keyboard = city_buttons(list(location_data.keys()))
            if keyboard:
                bot.send_message(message.from_user.id, 'Возможные варианты', reply_markup=keyboard)

        else:
            bot.send_message(message.from_user.id, 'Не удалось найти город по вашему запросу')
            cmd_start(message)

    else:
        bot.send_message(message.from_user.id, 'Обнаружена ошибка в названии города')
        cmd_start(message)


@bot.message_handler(commands=['start'])
def cmd_start(message: types.Message or types.CallbackQuery) -> None:
    """
    Функция команды /start
    """
    global first_start_flag
    global location_data

    location_data = {}

    if first_start_flag is True:
        bot.send_message(message.from_user.id, 'Начнём поиск предложений!')
        first_start_flag = False

    bot.send_message(message.from_user.id, 'Введите название города,'
                                           'в котором вы хотели бы остановиться')
    if isinstance(message, types.CallbackQuery):
        bot.register_next_step_handler(message.message, get_city)
    else:
        bot.register_next_step_handler(message, get_city)


def sending_results(msg: types.Message, some_dict: typing.Dict) -> None:
    """
    Функция отправляет все найденные предложения пользователю в ТГ
    """
    for elem in some_dict.keys():
        text = (f'Отель  :  {elem}\n'
                f'Адрес отеля  :  {some_dict[elem]["address"]}\n'
                f'Расстояние до центра города  :  {some_dict[elem]["distance"]}\n'
                f'Стоимость всего проживания  :  {some_dict[elem]["price"]}\n'
                f'Фото  :  {some_dict[elem]["photo_url"]}')
        bot.send_message(msg.chat.id, text)


@bot.message_handler(commands=['lowprice', 'highprice'])
def cmd_lowprice_highprice(message: types.Message) -> None:
    """
    Функция команд /lowprice ,  /highprice
    """
    if message.text[1:] in ('lowprice', 'highprice'):
        if message.text[1:] == 'lowprice':
            request_data['cmd'] = 'lowprice'
        else:
            request_data['cmd'] = 'highprice'

    if all(request_data.values()):
        bot.send_message(message.chat.id, 'Идёт обработка запроса')
        answer = hotels_search(request_data)
        sending_results(message, answer)

    else:
        if request_data['city'] == '':
            bot.send_message(message.from_user.id, 'Введите название города,'
                                                   'где вы хотели бы остановиться')
            bot.register_next_step_handler(message, get_city)


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
    :param message: сообщение любого типа,
    который не поддерживается данным ботом
    """
    bot.send_message(message.from_user.id,
                     'К сожалению, данный тип сообщение я не могу обработать :(\n'
                     'Для начала работы необходимо ввести '
                     'команду "/start". Для получения списка всех'
                     'доступных команд введите команду "/help"')


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0, timeout=1)
