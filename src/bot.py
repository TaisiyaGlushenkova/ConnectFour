import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import string

from src.room import Room

from src.bot_texts import *

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
        text=memo,
    )


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, greeting)
    help(message)


@bot.message_handler(commands=["rating"])
def rating(message):
    if message.from_user.id not in players_rating:
        bot.send_message(message.chat.id, text=error_no_rating)
        return
    text = "\n".join(
        result + " " + str(count)
        for result, count in players_rating[message.from_user.id].items()
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["new"])
def create_new_game(message):
    keyboard = InlineKeyboardMarkup()
    key_open = InlineKeyboardButton(text=open_game, callback_data="open")
    key_close = InlineKeyboardButton(text=close_game, callback_data="close")
    keyboard.row_width = 1
    keyboard.add(key_open, key_close)
    bot.send_message(
        message.chat.id,
        text=choose_game_type,
        reply_markup=keyboard,
    )


def check_code(message):
    code = message.text
    if code in invitors:
        m = bot.send_message(message.from_user.id, text=code_exists)
        bot.register_next_step_handler(m, check_code)
    else:
        invitors[code] = message.from_user.id
        m = bot.send_message(message.from_user.id, text=code_accepted)


@bot.callback_query_handler(func=lambda call: call.data == "close")
def create_close_game(call):
    bot.send_message(call.message.chat.id, text=make_up_code)
    bot.register_next_step_handler(call.message, check_code)


@bot.message_handler(commands=["join"])
def try_join(message):
    lst = message.text.split(" ")
    if len(lst) != 2:
        bot.send_message(message.chat.id, text=join_parse_error)
        return

    code = lst[1]

    if code in rooms:
        bot.send_message(
            message.from_user.id,
            text=code_exists,
        )
        return
    if code in invitors and invitors[code] == message.from_user.id:
        bot.send_message(message.from_user.id, text=join_yourself)
        return
    if code not in invitors:
        bot.send_message(message.from_user.id, text=game_not_exist)
        return
    rooms[code] = Room(invitors[code], message.from_user.id, code)
    rooms[code].create_boards(bot)


@bot.callback_query_handler(func=lambda call: call.data == "open")
def put_in_query(call):
    if call.from_user.id in waiting_players:
        bot.send_message(call.from_user.id, text=twice_in_queue)
        return
    if len(waiting_players) == 0:
        waiting_players.append(call.from_user.id)
        bot.send_message(
            call.from_user.id,
            text=wait_opponent,
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
        bot.send_message(call.from_user.id, text=game_not_exist)
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
