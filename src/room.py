from typing import Union

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.field import Field


def create_keyboard(field : Field, code : str) -> InlineKeyboardMarkup:
    """
    Create a keyboard for the given field and code.

    The keyboard is a single InlineKeyboardMarkup with buttons
    labeled with the values of the field. The callback data for
    each button is a string of the form "row column code".

    :param field: The Field object whose state is used as the
                  button labels.
    :param code: The string that is appended to the callback data
                 of each button.
    :return: The created InlineKeyboardMarkup.
    """
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = field.width
    for row in range(field.height):
        line = []
        for column in range(field.width):
            key = InlineKeyboardButton(
                text=field.field_storage[row][column],
                callback_data=str(row) + " " + str(column) + " " + code,
            )
            line.append(key)
        keyboard.add(*line)
    return keyboard


class Room:
    """
    Represents a game room for two players.

    Attributes:
        id1 (Union[int, str]): The ID of the first player.
        id2 (Union[int, str]): The ID of the second player.
        code (str): A code to identify the room.
        field (Field): The game field.
        message_1 (Optional[Message]): The message sent to the first player.
        message_2 (Optional[Message]): The message sent to the second player.
    """
    def __init__(self, id1 : Union[int, str], id2 : Union[int, str], code : str) -> None:
        """
        Initializes a new Room object.

        :param id1: The ID of the first player.
        :param id2: The ID of the second player.
        :param code: A code to identify the room.
        """
        self.id1 = id1
        self.id2 = id2
        self.code = code
        self.field = Field()
        self.message_1 = None
        self.message_2 = None
        
    def get_keyboard(self) -> InlineKeyboardMarkup:
        """
        Creates and returns an inline keyboard for the game field.

        :return: An inline keyboard for the game field.
        """
        return create_keyboard(self.field, self.code)

    def get_players_id(self) -> tuple[int, int]:
        """
        Returns a tuple of the player IDs in the room.

        :return: A tuple of two player IDs.
        """
        return self.id1, self.id2

    def create_boards(self, bot : TeleBot) -> None:
        """
        Sends a message to both players with an inline keyboard representing
        the game board.

        :param bot: The bot used to send the messages.
        :type bot: TeleBot
        """
        self.message_1 = bot.send_message(
            chat_id=self.id1,
            text="The game has started. Your symbol is x",
            reply_markup=self.get_keyboard(),
        )
        self.message_2 = bot.send_message(
            chat_id=self.id2,
            text="The game has started. Your symbol is o",
            reply_markup=self.get_keyboard(),
        )

    def put_symbol(self, user_id : Union[int, str], cord : tuple[int, int], bot : TeleBot) -> int:
        """
        Processes a move in the game.

        :param user_id: The ID of the player who made the move.
        :type user_id: int or str
        :param cord: The coordinates of the cell where the move was made.
        :type cord: tuple of two ints
        :param bot: The bot used to edit the messages with the game field.
        :type bot: TeleBot
        :return: 0 if the move was successful, 1 if the move was invalid, -1 if the game ended in a draw, -2 if the game ended with a win.
        :rtype: int
        """
        whose_move_id = self.id2 if self.field.full_cells_count % 2 == 1 else self.id1
        opponent_id = self.id1 if self.id1 != whose_move_id else self.id2
        if whose_move_id != user_id:
            return 1
        if self.field.make_move(cord[0], cord[1]) == -1:
            return 1

        for msg in [self.message_1, self.message_2]:
            try:
                bot.edit_message_text(
                    text="It's your turn"
                    if msg.chat.id != whose_move_id
                    else "It's opponent's turn",
                    chat_id=msg.chat.id,
                    message_id=msg.id,
                    reply_markup=self.get_keyboard(),
                )
            except Exception as e:
                print(e)

        is_game_over, cord_begin, _ = self.field.is_game_over()
        if is_game_over:
            if cord_begin == (-1, -1):
                for id in self.get_players_id():
                    bot.send_message(chat_id=id, text="DRAW")
                return_value = -1
            else:
                bot.send_message(chat_id=whose_move_id, text="YOU WON")
                bot.send_message(chat_id=opponent_id, text="YOU LOST")
                return_value = -2
            return return_value

        return 0
