import unittest
from unittest.mock import patch, MagicMock

import src.bot
from src.room import Room

from src.bot_texts import (
    memo,
    greeting,
    error_no_rating,
    open_game,
    close_game,
    choose_game_type,
    code_exists,
    code_accepted,
    make_up_code,
    game_not_exist,
    wait_opponent,
    join_yourself,
    join_parse_error,
)


class TestBot(unittest.TestCase):
    def setUp(self):
        pass

    def test_generate_code(self):
        src.bot.generate_new_code()

    @patch("telebot.TeleBot.send_message")
    def test_help(self, send_message_mock):
        message = MagicMock()
        message.chat.id = 0
        src.bot.help(message)
        self.assertEqual(send_message_mock.call_count, 1)
        call_args, call_kwargs = send_message_mock.call_args
        self.assertIn(memo, call_kwargs["text"])

    @patch("telebot.TeleBot.send_message")
    def test_rating(self, send_message_mock):
        message = MagicMock()
        message.chat.id = 0
        src.bot.rating(message)
        call_args, call_kwargs = send_message_mock.call_args
        self.assertEqual(send_message_mock.call_count, 1)
        self.assertIn(error_no_rating, call_kwargs["text"])

    @patch("telebot.TeleBot.send_message")
    def test_new_game(self, send_message_mock):
        message = MagicMock()
        message.chat.id = 0
        src.bot.create_new_game(message)
        call_args, call_kwargs = send_message_mock.call_args
        self.assertEqual(send_message_mock.call_count, 1)
        self.assertIn(choose_game_type, call_kwargs["text"])

    @patch("telebot.TeleBot.send_message")
    def test_check_code(self, send_message_mock):
        message = MagicMock()
        message.chat.id = 0
        message.text = "code"
        src.bot.check_code(message)
        call_args, call_kwargs = send_message_mock.call_args
        self.assertEqual(send_message_mock.call_count, 1)
        self.assertIn(code_accepted, call_kwargs["text"])

    @patch("telebot.TeleBot.send_message")
    def test_join(self, send_message_mock):
        message = MagicMock()
        message.chat.id = 0
        message.from_user.id = 0
        message.text = "/join code"

        src.bot.invitors = {}
        src.bot.rooms = {"code": Room(0, 1, "code")}
        src.bot.try_join(message)
        call_args, call_kwargs = send_message_mock.call_args
        self.assertEqual(send_message_mock.call_count, 1)
        self.assertIn(code_exists, call_kwargs["text"])

        src.bot.invitors = {"code": 0}
        src.bot.rooms = {}
        src.bot.try_join(message)
        call_args, call_kwargs = send_message_mock.call_args
        self.assertEqual(send_message_mock.call_count, 2)
        self.assertIn(join_yourself, call_kwargs["text"])

        src.bot.invitors = {}
        src.bot.rooms = {}
        src.bot.try_join(message)
        call_args, call_kwargs = send_message_mock.call_args
        self.assertEqual(send_message_mock.call_count, 3)
        self.assertIn(game_not_exist, call_kwargs["text"])

        src.bot.invitors = {"code": 1}
        src.bot.rooms = {}
        src.bot.try_join(message)
        call_args, call_kwargs = send_message_mock.call_args
        self.assertEqual(send_message_mock.call_count, 5)

    @patch("telebot.TeleBot.send_message")
    def test_query(self, send_message_mock):
        src.bot.waiting_players = []
        call = MagicMock()
        call.from_user.id = 0
        call.data = "open"
        src.bot.put_in_query(call)
        self.assertEqual(send_message_mock.call_count, 1)
        call_args, call_kwargs = send_message_mock.call_args
        self.assertIn(wait_opponent, call_kwargs["text"])

        call.from_user.id = 1
        call.data = "open"
        src.bot.put_in_query(call)
        self.assertEqual(send_message_mock.call_count, 3)

        self.assertEqual(len(src.bot.waiting_players), 0)

    def test_add_game(self):
        src.bot.add_game(0, "WIN")
        src.bot.add_game(0, "LOSE")
        src.bot.add_game(0, "DRAW")
        self.assertEqual(src.bot.players_rating[0], {"WIN": 1, "LOSE": 1, "DRAW": 1})

    @patch("telebot.TeleBot.edit_message_text")
    def test_process_move(self, edit_message_mock):
        call = MagicMock()
        call.data = "0 0 code"
        call.from_user.id = 0
        src.bot.rooms = {}
        src.bot.rooms["code"] = MagicMock()
        src.bot.rooms["code"].put_symbol = MagicMock(return_value=-1)
        src.bot.rooms["code"].get_players_id = MagicMock(return_value=[0, 1])
        src.bot.players_rating = {}
        src.bot.process_move(call)
        self.assertEqual(edit_message_mock.call_count, 0)
        self.assertEqual(src.bot.players_rating[0]["DRAW"], 1)
        self.assertEqual(src.bot.players_rating[1]["DRAW"], 1)

        src.bot.rooms["code"] = Room(0, 1, "code")
        src.bot.rooms["code"].message_1 = MagicMock()
        src.bot.rooms["code"].message_1.chat.id = 0
        src.bot.rooms["code"].message_2 = MagicMock()
        src.bot.rooms["code"].message_1.chat.id = 1
        src.bot.process_move(call)
        self.assertEqual(edit_message_mock.call_count, 2)
