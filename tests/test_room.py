import unittest

from src.room import Room

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.field import Field


class MockChat:
    def __init__(self, id):
        self.id = id


class MockMessage:
    def __init__(self, chat, id, text):
        self.chat = chat
        self.id = id
        self.text = text


class MockBot:
    def __init__(self):
        pass

    def send_message(self, chat_id, text, reply_markup=None):
        return MockMessage(MockChat(chat_id), 0, text)

    def edit_message_text(self, chat_id, message_id, text, reply_markup):
        pass


class RoomTest(unittest.TestCase):
    def setUp(self):
        self.room = Room(1, 2, "some_random_code")
        self.bot = MockBot()

    def tearDown(self):
        return super().tearDown()

    def test_get_keyboard(self):
        markup = self.room.get_keyboard()
        self.assertIsInstance(markup, InlineKeyboardMarkup)
        self.assertEqual(markup.row_width, self.room.field.width)
        self.assertEqual(len(markup.keyboard), self.room.field.height)
        for row in range(self.room.field.height):
            for column in range(self.room.field.width):
                self.assertIsInstance(
                    markup.keyboard[row][column], InlineKeyboardButton
                )
                self.assertEqual(
                    str(row) + " " + str(column) + " " + self.room.code,
                    markup.keyboard[row][column].callback_data,
                )
                self.assertEqual(
                    self.room.field.field_storage[row][column],
                    markup.keyboard[row][column].text,
                )

    def test_get_players_id(self):
        self.assertEqual(self.room.get_players_id(), (1, 2))

    def test_create_boards(self):
        self.room.create_boards(self.bot)
        self.assertEqual(
            self.room.message_1.text, "The game has started. Your symbol is x"
        )
        self.assertEqual(
            self.room.message_2.text, "The game has started. Your symbol is o"
        )

    def test_put_symbol(self):
        self.assertEqual(self.room.put_symbol(1, (0, 0), self.bot), 0)
