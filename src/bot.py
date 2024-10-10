import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import string

from src.room import Room

from config import TOKEN

bot = telebot.TeleBot(TOKEN)

invitors = {}

players_rating = {}

waiting_players = []

rooms = {}


def generate_new_code():
    code = ""
    while code in rooms:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=20))
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=20))


@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(
        message.chat.id,
        text="""
                    Нажми:
                    /start для приветствия\n
                    /help чтобы вывести эту памятку\n
                    /rating для просмотра рейтинга\n
                    /new для создания новой игры\n
                    /join *code* если друг тебе прислал кодовое слово
                    """,
    )


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Привет, я бот для игры в четыре в ряд")
    help(message)


@bot.message_handler(commands=["rating"])
def callback_rating(message):
    if message.from_user.id not in players_rating:
        bot.send_message(message.chat.id, text="Вы ещё не играли")
        return
    text = "\n".join(
        result + " " + str(count)
        for result, count in players_rating[message.from_user.id].items()
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["new"])
def callback_new_game(message):
    keyboard = InlineKeyboardMarkup()
    key_open = InlineKeyboardButton(text="Find me an opponent", callback_data="open")
    key_close = InlineKeyboardButton(text="Invite a friend", callback_data="close")
    keyboard.row_width = 1
    keyboard.add(key_open, key_close)
    bot.send_message(
        message.chat.id,
        text="Выберите тип игры",
        reply_markup=keyboard,
    )


def callback_sign_up(message):
    code = message.text
    if code in invitors:
        m = bot.send_message(message.from_user.id, text="Это кодовое слово уже занято")
        bot.register_next_step_handler(m, callback_sign_up)
    else:
        invitors[code] = message.from_user.id
        m = bot.send_message(
            message.from_user.id, text="Отлично, теперь пришли код другу"
        )


@bot.callback_query_handler(func=lambda call: call.data == "close")
def create_close_game(call):
    bot.send_message(call.message.chat.id, text="Придумай кодовое слово")
    bot.register_next_step_handler(call.message, callback_sign_up)


def get_room_number(id):
    for i in range(len(rooms)):
        if rooms[i].id1 == id or rooms[i].id2 == id:
            return i
    return -1


@bot.message_handler(commands=["join"])
def callback_join(message):
    lst = message.text.split(" ")
    if len(lst) != 2:
        bot.send_message(
            message.chat.id, text="Нужно ввести кодовое слово. Example: /join code"
        )
        return

    code = lst[1]
    if code not in invitors:
        bot.send_message(message.from_user.id, text="Это кодовое слово не существует")
        return
    elif code in rooms:
        bot.send_message(
            message.from_user.id,
            text="Эта игра уже началась. Попросите друга прислать новое кодовое слово",
        )
        return
    elif invitors[code] == message.from_user.id:
        bot.send_message(message.from_user.id, text="You can not play with yourself")
        return
    rooms[code] = Room(invitors[code], message.from_user.id, code)
    rooms[code].create_boards(bot)


@bot.callback_query_handler(func=lambda call: call.data == "open")
def put_in_query(call):
    if call.from_user.id in waiting_players:
        bot.send_message(call.from_user.id, text="Вы уже в очереди")
        return
    if len(waiting_players) == 0:
        waiting_players.append(call.from_user.id)
        bot.send_message(
            call.from_user.id,
            text="Ожидайте",
        )
    else:
        opponent_id = waiting_players[-1]
        waiting_players.pop()
        code = generate_new_code()

        rooms[code] = Room(call.from_user.id, opponent_id, code)
        rooms[code].create_boards(bot)


def add_game(id, result):
    if id not in players_rating:
        players_rating[id] = {"WIN": 0, "LOSE": 0, "DRAW": 0}
    players_rating[id][result] += 1


@bot.callback_query_handler(func=lambda call: True)
def process_move(call):
    row, column, code = call.data.split(" ")
    row = int(row)
    column = int(column)
    if code not in rooms:
        bot.send_message(call.from_user.id, text="Эта игра закончилась")
        return
    exit_code = rooms[code].put_symbol(call.from_user.id, (row, column), bot)

    if exit_code < 0:
        players_id = rooms[code].get_players_id()
        rooms.pop(code)
        if exit_code == -1:
            for id in players_id:
                add_game(id, "DRAW")
        else:
            opponent_id = (
                players_id[0] if players_id[0] != call.from_user.id else players_id[1]
            )
            add_game(call.from_user.id, "WIN")
            add_game(opponent_id, "LOSE")
