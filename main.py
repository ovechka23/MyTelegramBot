# подключение библиотеки telebot
import telebot
# подключение  классов ReplyKeyboardMarkup и KeyboardButton из модуля types для создания пользовательских клавиатур и кнопок на клавиатуре соответсвенно
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
# подключение модуль random, который используется для генерации случайных чисел
import random


# создаем объект бота с указанным токеном
bot = telebot.TeleBot('My_Token')

# словарь с текущим состоянием игры для каждого пользователя
games = {}

# функция, которая обрабатывает сообщения пользователя
@bot.message_handler(commands=['start'])
def start_game(message):
    # проверяем, не начал ли пользователь уже игру
    if message.chat.id in games:
        bot.send_message(message.chat.id, 'Вы уже начали игру.')
        return
    # генерируем клавиатуру для выбора игры
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Играть в крестики-нолики'))
    keyboard.add(KeyboardButton('Играть в камень-ножницы-бумага'))

    # отправляем сообщение с инструкциями и клавиатурой
    bot.send_message(message.chat.id, 'Добро пожаловать! Выберите игру:', reply_markup=keyboard)

# функция, которая обрабатывает сообщения пользователя с выбором игры
@bot.message_handler(func=lambda message: message.chat.id not in games and
                                              message.text in ['Играть в крестики-нолики', 'Играть в камень-ножницы-бумага'])
def choose_game(message):
    if message.text == 'Играть в крестики-нолики':
        start_tic_tac_toe(message)
    elif message.text == 'Играть в камень-ножницы-бумага':
        start_stoun_scissors_paper(message)

# функция, которая начинает игру в крестики-нолики
def start_tic_tac_toe(message):
    # создаем новую игру
    games[message.chat.id] = {
        'board': [[' '] * 3 for _ in range(3)],
        'turn': 'X'
    }

    # генерируем клавиатуру для выбора ячейки
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for row in range(3):
        keyboard.row(*(KeyboardButton(f"{row+1} {col+1}") for col in range(3)))

    # отправляем сообщение с инструкциями и клавиатурой
    bot.send_message(message.chat.id, 'Добро пожаловать в игру крестики-нолики! '
                                      'Чтобы сделать ход, нажмите на соответствующую кнопку на клавиатуре. '
                                      'Вы играете за крестики (X), ваш противник играет за нолики (O).\n\n'
                                      'Сейчас ходят крестики.', reply_markup=keyboard)

# функция, которая проверяет выигрышную комбинацию на игровом поле
def check_winner(board):
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != ' ':
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != ' ':
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] != ' ':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != ' ':
        return board[0][2]
    return None

# функция, которая отображает игровое поле в виде текстовой строки
def board_to_string(board):
    return '\n'.join([' | '.join(row) for row in board])

# обработчик кнопок "Новая игра" и "Выход в меню" после окончания игры
def end_game_keyboard(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Новая игра'))
    keyboard.add(KeyboardButton('Выход в меню'))
    bot.send_message(message.chat.id, 'Выберите дальшейшие действия: ', reply_markup=keyboard)

# обработчик кнопки "Новая игра"
@bot.message_handler(func=lambda message: message.chat.id not in games and message.text == 'Новая игра')
def new_game(message):
    start_tic_tac_toe(message)

# обработчик кнопки "Выход в меню"
@bot.message_handler(func=lambda message: message.chat.id not in games and message.text == 'Выход в меню')
def exit_game(message):
    start_game(message)

# функция, которая обрабатывает сообщения пользователя с координатами хода
@bot.message_handler(func=lambda message: message.chat.id in games and games[message.chat.id]['turn'] == 'X')
def make_move(message):
    try:
        # получаем координаты хода из текста сообщения
        row, col = [int(x) - 1 for x in message.text.split()]
        if not (0 <= row < 3 and 0 <= col < 3):
            raise ValueError()
    except:
        bot.send_message(message.chat.id, 'Некорректный ввод. Пожалуйста, выберите ячейку на клавиатуре.')
        return

    # получаем текущее состояние игры
    game = games[message.chat.id]

    # проверяем, что клетка свободна
    if game['board'][row][col] != ' ':
        bot.send_message(message.chat.id, 'Эта клетка уже занята. Пожалуйста, выберите другую клетку.')
        return

    # делаем ход
    game['board'][row][col] = 'X'

    # проверяем, есть ли победитель
    winner = check_winner(game['board'])
    if winner is not None:
        del games[message.chat.id]
        bot.send_message(message.chat.id, 'Вы выиграли! Игра окончена.\n\n' + board_to_string(game['board']))
        end_game_keyboard(message)
        return

        # проверяем, остались ли свободные клетки
    elif all(' ' not in row for row in game['board']):
        del games[message.chat.id]
        bot.send_message(message.chat.id, 'Ничья! Игра окончена.\n\n' + board_to_string(game['board']))
        end_game_keyboard(message)
        return

    else:
        # передаем ход противнику
        game['turn'] = 'O'

        # генерируем клавиатуру для выбора ячейки
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for row in range(3):
            keyboard.row(*(KeyboardButton(f"{row+1} {col+1}") for col in range(3)))

        # отправляем сообщение о текущем состоянии игры и клавиатурой новому игроку
        bot.send_message(message.chat.id, f'Вы сделали ход:\n\n{board_to_string(game["board"])}\n\n'
                                      'Сейчас ходят нолики.', reply_markup=keyboard)
# функция, которая обрабатывает сообщения пользователя с координатами хода
@bot.message_handler(func=lambda message: message.chat.id in games and games[message.chat.id]['turn'] == 'O')
def make_move_auto(message):
    # получаем координаты хода из текста сообщения
    try:
        row, col = [int(x) - 1 for x in message.text.split()]
        if not (0 <= row < 3 and 0 <= col < 3):
            raise ValueError()
    except:
        bot.send_message(message.chat.id, 'Некорректный ввод. Пожалуйста, выберите ячейку на клавиатуре.')
        return

    # получаем текущее состояние игры
    game = games[message.chat.id]

    # проверяем, что клетка свободна
    if game['board'][row][col] != ' ':
        bot.send_message(message.chat.id, 'Эта клетка уже занята. Пожалуйста, выберите другую клетку.')
        return

    # делаем ход
    game['board'][row][col] = 'O'

    # проверяем, есть ли победитель
    winner = check_winner(game['board'])
    if winner is not None:
        if winner is not None:
            del games[message.chat.id]
            bot.send_message(message.chat.id, 'Вы проиграли! Игра окончена.\n\n' + board_to_string(game['board']))
            end_game_keyboard(message)
            return

            # проверяем, остались ли свободные клетки
        if all(' ' not in row for row in game['board']):
            del games[message.chat.id]
            bot.send_message(message.chat.id, 'Ничья! Игра окончена.\n\n' + board_to_string(game['board']))
            end_game_keyboard(message)
            return

    # передаем ход противнику
    game['turn'] = 'X'

    # генерируем клавиатуру для выбора ячейки
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for row in range(3):
        keyboard.row(*(KeyboardButton(f"{row+1} {col+1}") for col in range(3)))

    # отправляем сообщение о текущем состоянии игры и клавиатурой новому игроку
    bot.send_message(message.chat.id, f'Противник сделал ход:\n\n{board_to_string(game["board"])}\n\n'
                                  'Ваш ход. Вы играете за крестики (X).', reply_markup=keyboard)


# Функция, которая запускает игру в "Камень-ножницы-бумага"
def start_stoun_scissors_paper(message):
    # Создаем клавиатуру с кнопками "камень", "ножницы" и "бумага"
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=3)
    button_rock = telebot.types.KeyboardButton('Камень')
    button_scissors = telebot.types.KeyboardButton('Ножницы')
    button_paper = telebot.types.KeyboardButton('Бумага')
    keyboard.add(button_rock, button_scissors, button_paper)

    # Отправляем сообщение с клавиатурой
    bot.send_message(message.chat.id, "Выбери свой ход:", reply_markup=keyboard)

    # Регистрируем функцию, которая будет вызвана при получении ответа пользователя
    bot.register_next_step_handler(message, play_game)

# Определяем функцию, которая будет вызвана при получении ответа пользователя на выбор хода
def play_game(message):
    # Получаем выбранный игроком ход и генерируем случайный ход для компьютера
    player_move = message.text.lower()
    computer_move = random.choice(['камень', 'ножницы', 'бумага'])

    # Определяем победителя
    if player_move == 'камень' and computer_move == 'ножницы':
        winner = 'Игрок'
    elif player_move == 'ножницы' and computer_move == 'бумага':
        winner = 'Игрок'
    elif player_move == 'бумага' and computer_move == 'камень':
        winner = 'Игрок'
    elif player_move == computer_move:
        winner = 'Никто'
    else:
        winner = 'Компьютер'

    # Отправляем сообщение с результатом игры
    bot.send_message(message.chat.id,
                     f"Твой выбор: {player_move}\nХод компьютера: {computer_move}\nПобедитель: {winner}")
    end_KMP_keyboard(message)

def end_KMP_keyboard(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Играть заново'))
    keyboard.add(KeyboardButton('Выход в меню'))
    bot.send_message(message.chat.id, 'Выберите дальшейшие действия: ', reply_markup=keyboard)

# обработчик кнопки "Играть заново"
@bot.message_handler(func=lambda message: message.text == 'Играть заново')
def new_game(message):
    start_stoun_scissors_paper(message)

#запускаем бота
bot.polling()
