from typing import List
from telebot.types import Message

from src.bot import *


def listener(messages: List[Message]) -> None:
    for m in messages:
        print(str(m))


if __name__ == "__main__":
    bot.set_update_listener(listener)
    bot.infinity_polling()
