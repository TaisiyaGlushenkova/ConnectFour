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


def generate_new_code() -> str:
    """
    Generates a new unique code of length 20.

    :return: The new code
    :rtype: str
    """
    code = ""
    while code in rooms:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=20))
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=20))


@bot.message_handler(commands=["help"])
def help(message: telebot.types.Message) -> None:
    """
    Handles the /help command.

    Sends a message containing the text from memo to the user.

    :param message: The message object containing the command.
    :type message: telebot.types.Message
    """
    bot.send_message(
        message.chat.id,
        text=memo,
    )


@bot.message_handler(commands=["start"])
def start(message: telebot.types.Message) -> None:
    """
    Handles the /start command.

    Sends a greeting message and the help message to the user.

    :param message: The message object containing the command.
    :type message: telebot.types.Message
    """
    bot.send_message(message.chat.id, greeting)
    help(message)


@bot.message_handler(commands=["rating"])
def rating(message: telebot.types.Message) -> None:
    """
    Handles the /rating command.

    Sends a message containing the player's rating to the user.

    The rating is a dictionary with the following keys:
        - "WIN": The number of wins.
        - "DRAW": The number of draws.
        - "LOSE": The number of losses.

    :param message: The message object containing the command.
    :type message: telebot.types.Message
    """
    if message.from_user.id not in players_rating:
        bot.send_message(message.chat.id, text=error_no_rating)
        return
    text = "\n".join(
        result + " " + str(count)
        for result, count in players_rating[message.from_user.id].items()
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["new"])
def create_new_game(message: telebot.types.Message) -> None:
    """
    Handles the /new command.

    Sends a message with two buttons: for open game and for close game.
    The "open" button allows the player to get in line,
    and the "close" button allows to create a closed game.

    :param message: The message object containing the command.
    :type message: telebot.types.Message
    """
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


def check_code(message: telebot.types.Message) -> None:
    """
    Checks the code sent by the user.

    If the code is already booked, notifies the user about that.
    If the code is available, adds the code to invitors and sends a message about success.

    :param message: The message object containing the code.
    :type message: telebot.types.Message
    """
    code = message.text
    if code in invitors:
        m = bot.send_message(message.from_user.id, text=code_exists)
        bot.register_next_step_handler(m, check_code)
    else:
        invitors[code] = message.from_user.id
        m = bot.send_message(message.from_user.id, text=code_accepted)


@bot.callback_query_handler(func=lambda call: call.data == "close")
def create_close_game(call: telebot.types.CallbackQuery) -> None:
    """
    Handles the "close" button.

    Asks the user to enter a code to invite another player.
    """
    bot.send_message(call.message.chat.id, text=make_up_code)
    bot.register_next_step_handler(call.message, check_code)


@bot.message_handler(commands=["join"])
def try_join(message: telebot.types.Message) -> None:
    """
    Handles the /join command.

    Checks the code for validity and that the user is not trying to join his own game.
    If the code is valid and the user is not the invitor, creates a new Room object and
    sends a message to both players with an inline keyboard representing the game field.

    :param message: The message object containing the code.
    :type message: telebot.types.Message
    """
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
def put_in_query(call: telebot.types.CallbackQuery) -> None:
    """
    Handles the "open" button.

    Checks if the user is already in the waiting queue. If yes, sends a message about
    that. If not, adds the user to the waiting queue and sends a message about waiting
    for an opponent. If another user is already in the waiting queue, creates a new
    Room object, removes both players from the waiting queue, and sends a message to
    both players with an inline keyboard representing the game field.

    :param call: The callback query object containing the user ID.
    :type call: telebot.types.CallbackQuery
    """
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


def add_game(id, result: str) -> None:
    """
    Adds a game result to the player's rating.

    The result must be either "WIN", "LOSE", or "DRAW". If the player ID is not
    already in the players_rating dictionary, a new entry is created with all
    values set to 0. The corresponding value in the dictionary is then incremented
    by 1.

    :param id: The ID of the player.
    :type id: int
    :param result: The result of the game.
    :type result: str
    """
    if id not in players_rating:
        players_rating[id] = {"WIN": 0, "LOSE": 0, "DRAW": 0}
    players_rating[id][result] += 1


@bot.callback_query_handler(func=lambda call: True)
def process_move(call: telebot.types.CallbackQuery) -> None:
    """
    Handles a move in the game.

    The call data must look like \"row column code\".
    The row and column values must be integers. The code identifies the room.
    If there is no room with that code, notifies the user. If the move is invalid, does nothing.
    If the move is valid, processes the move. Also checks if game is over. If it is, recalculates the ratings.

    Parameters:
        call (telebot.types.CallbackQuery): The callback query object containing the user ID and move data.
    """
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
