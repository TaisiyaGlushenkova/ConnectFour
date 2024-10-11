# ConnectFour
TL;DR connect four game in telegram bot
Author: Глушенкова Таисия Николаевна, Б05-327

## Функционал
/start запуск бота

/help даёт справку о боте

/new начать новую игру

/join *code* чтобы присоединиться к игре, созданной другом

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

**Алгоритм работы бота для игры "Четыре в ряд"**

Когда приходит сообщение, бот обрабатывает его и выбирает соответсвующий ответ. Бот предоставляет следующие команды:

/start --- вывод приветствия и памятки

/help --- вывод памятки

/rating --- вывод результатов игрока

/new --- для создания новой игры

/join arg --- чтобы присоединиться к игре с кодовым словом arg

Когда оба игрока присоединяются, создаётся "комната" и поле для игры. Обоим участникам приходит сообщение с клавиатурой имитирующей поле. По окончанию игры бот оглашает её результаты.

В течение всего времени работы поддерживаются 

* очередь игроков, ищущих соперника
* действующие приглашения к игре
* текущие игры
* результаты игроков (при перезапуске бота они обнуляются)

Во многом реализована защита от некорректных действий пользователей.

## Используемые технологии
python3 --- Разработка
telebot --- Telegram API
unittest --- Тестирование

Бот не тестировался на версиях Python ранее 3.10.0
Unit-тесты не проводились на версиях Python ранее 3.12.3

## Запуск
В корневой директории создайте файл config.py и поместите токен бота в файл config.py в root директории в виде
TOKEN = "ваш токен"
Установите библиотеки из requirements.txt (pip install -r requirements.txt)
Запустите main.py

## Процент покрытия тестами
с помощью nosetests
![image](https://github.com/user-attachments/assets/ebd48977-685d-4746-9b4f-450fbe9dceaa)

