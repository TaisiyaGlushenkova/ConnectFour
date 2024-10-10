from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.field import Field


def create_keyboard(field, code):
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
    def __init__(self, id1, id2, code):
        self.id1 = id1
        self.id2 = id2
        self.code = code
        self.field = Field()
        self.message_1 = None
        self.message_2 = None

    def get_keyboard(self):
        return create_keyboard(self.field, self.code)

    def get_players_id(self):
        return self.id1, self.id2

    def create_boards(self, bot):
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

    def put_symbol(self, user_id, cord, bot):
        whose_move_id = self.id2 if self.field.full_cells_count % 2 == 1 else self.id1
        opponent_id = self.id1 if self.id1 != whose_move_id else self.id2
        if whose_move_id != user_id:
            return 0
        if self.field.make_move(cord[0], cord[1]) == -1:
            return 0

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
