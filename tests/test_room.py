import unittest

from unittest.mock import MagicMock, patch

from src.room import Room

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.field import Field


class RoomTest(unittest.TestCase):
    def setUp(self):
        self.room = Room(1, 2, "code")
        self.room.message_1 = MagicMock()
        self.room.message_1.text = "text"
        self.room.message_1.message.chat.id = 1
        self.room.message_2 = MagicMock()
        self.room.message_2.text = "text"
        self.room.message_2.message.chat.id = 2

    def tearDown(self):
        pass

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

    @patch("telebot.TeleBot.send_message")
    def test_create_boards(self, send_message_mock):
        bot = MagicMock()
        bot.send_message = send_message_mock
        self.room.create_boards(bot)
        self.assertEqual(send_message_mock.call_count, 2)
        call_args, call_kwargs = send_message_mock.call_args
        self.assertEqual("The game has started. Your symbol is o", call_kwargs["text"])

    @patch("telebot.TeleBot.edit_message_text")
    def test_put_symbol(self, edit_message_text_mock):
        bot = MagicMock()
        bot.edit_message_text = edit_message_text_mock
        self.assertEqual(self.room.put_symbol(1, (0, 0), bot), 0)
        self.assertEqual(edit_message_text_mock.call_count, 2)
