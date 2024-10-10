# ConnectFour
TL;DR connect four game in telegram bot

## Функционал
/start запуск бота

/help даёт справку о боте

/play начать новую игру

/rating таблица результатов

Пользователь может пригласить конкретного соперника или попросить бота найти. Игра заканчивается, когда 4 фишки одного цвета собираются в ряд.

## Архитектура
### Классы
**Поле:**

Поля: длина, высота, количество заполненных клеток, хранилище (текущее состояние)

Методы: сделать ход, ответить закончена ли игра

**Игра/Матч**

Поля: id игры, id игроков, id сообщений с полем, поле

Методы: запросить поля, создать поля для игры, сделать ход

**Бот для игры "Четыре в ряд"**

Методы: приветствует, выводит памятку, создаёт игру с выбранным оппонентом/ищет оппонена среди других желающих, имитирует игру 4 в ряд, выводит таблицу результатов

## Используемые технологии
telebot --- Telegram API

unittest --- Тестирование

##Запуск
Поместите токен бота в файл config.py в root директории в виде
TOKEN = "ваш токен"
Установите библиотеки из requirements.txt
Запустите main.py
