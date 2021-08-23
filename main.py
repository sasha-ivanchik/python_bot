import telebot
from telebot import types
# import requests
from _config import TG_TOKEN
import typing

bot = telebot.TeleBot(TG_TOKEN)

commands_list: typing.List[str] = ['start', 'help', 'lowprice', 'highprice',
                                   'bestdeal', 'history', 'hello-world']

not_handling_messages: typing.List[str] = ['audio', 'document', 'photo', 'sticker',
                                           'video', 'video_note', 'voice', 'location', 'contact',
                                           'new_chat_members', 'left_chat_member',
                                           'new_chat_title', 'new_chat_photo', 'delete_chat_photo',
                                           'group_chat_created', 'supergroup_chat_created',
                                           'channel_chat_created', 'migrate_to_chat_id',
                                           'migrate_from_chat_id', 'pinned_message']

USERS_ID = set()


@bot.message_handler(commands=['start'])
def cmd_start(message: types.Message) -> None:
    """
    функция - команда старт
    выводит сообщение-приглашение и так же выводит
    кнопки доступных функций
    """
    markup = types.InlineKeyboardMarkup()
    item_help = types.InlineKeyboardButton(text='/help',
                                           callback_data='/help')
    item_hello_world = types.InlineKeyboardButton(text='/hello_world',
                                                  callback_data='/hello_world')

    markup.add(item_help, item_hello_world)
    bot.send_message(message.from_user.id,
                     'Введите возможную команду или нажмите на нужную кнопку',
                     reply_markup=markup)


@bot.message_handler(commands=['hello_world'])
def cmd_hello_world(message: types.Message) -> None:
    """
    тестовая функция для команды /hello_world.
    при вызове возвращает сообщение hello world
    """
    bot.send_message(message.from_user.id, 'hello world!')
    bot.send_message(message.from_user.id, 'введите /start для продолжения работы')


@bot.message_handler(commands=['help'])
def cmd_help(message: types.Message) -> None:
    """
    Функция для команды /help
    при вызове возвращает сообщение со списком
    всех доступных функций
    """
    str_commands: str = '/start - начало работы бота\n' \
                        '/help - список все доступных команд\n' \
                        '/hello_world - тестовая команда, выводит сообщение "hello world"\n' \
                        '/lowprice - в разработке\n' \
                        '/highprice - в разработке\n' \
                        '/bestdeal - в разработке\n' \
                        '/history - в разработке'
    bot.send_message(message.from_user.id, str_commands)


@bot.callback_query_handler(func=lambda call: True)
def cmd_on_button(call: types.CallbackQuery):
    """
    функция для обработки события нажатия на кнопку команды
    в меню команды /start
    """
    if call.data == '/help':
        bot.send_message(call.message.chat.id, '/start - начало работы бота\n'
                                               '/help - список все доступных команд\n'
                                               '/hello_world - тестовая команда, выводит сообщение "hello world"\n'
                                               '/lowprice - в разработке\n'
                                               '/highprice - в разработке\n'
                                               '/bestdeal - в разработке\n'
                                               '/history - в разработке')
        # cmd_help(call.message)
    elif call.data == '/hello_world':
        bot.send_message(call.message.chat.id, 'hello world!')


@bot.message_handler(content_types=['text'])
@bot.edited_message_handler(content_types=['text'])
def greeting(message: types.Message) -> None:
    """
    Функция-обработчик текстовых сообщений.
    Отправляет приветственное сообщение
    в ответ на сообщение "Привет"
    :param message: сообщение присланное пользователем
    :return: ответное сообщение с приветствием
    """
    replay: str = '\nДля начала работы необходимо ввести ' \
                  'команду "/start". Для получения списка всех ' \
                  'доступных команд введите команду "/help"'

    if message.text.lower().startswith('/') is False \
            and message.text.lower() == 'привет':
        if message.from_user.id not in USERS_ID:
            first_replay: str = 'Привет!' + replay
            bot.send_message(message.from_user.id, first_replay)
        else:
            second_replay = 'Привет еще раз!' + replay
            bot.send_message(message.from_user.id, second_replay)

    elif message.text.lower().startswith('/') is False \
            and message.text.lower() != 'привет':
        flood_replay = 'Меньше слов больше дела!' + replay
        if message.from_user.id not in USERS_ID:
            first_flood_replay = "Привет! \n" + flood_replay
            bot.send_message(message.from_user.id, first_flood_replay)
        else:
            bot.send_message(message.from_user.id, flood_replay)

    elif message.text.lower().startswith('/') and \
            message.text.lower()[1:] not in commands_list:
        print(message.text.lower()[1:])
        bot.send_message(message.from_user.id,
                         'Команда введена некорректно.'
                         'Повторите ввод или воспользуйтесь кнопкой!')
    USERS_ID.add(message.from_user.id)


@bot.message_handler(content_types=not_handling_messages)
def get_unhandling_msg(message: types.Message):
    """
    Функция обработчик сообщений неподдерживаемых типов.
    :param message: сообщение любого типа,
    который не поддерживается данным ботом
    :return: сообщение пользователю о необработанном запросе
    """
    bot.send_message(message.from_user.id,
                     'К сожалению, данный тип сообщение я не могу обработать :(\n'
                     'Для начала работы необходимо ввести '
                     'команду "/start". Для получения списка всех'
                     'доступных команд введите команду "/help"')


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
