import os

import logging
import telebot
from telebot import types

from sqlalchemy.orm import Session
from sqlalchemy import select

from engine import engine
from models import User, Messages

TOKEN = os.environ.get('TOKEN')  # Считываем токен из переменных среды
bot = telebot.TeleBot(TOKEN)  # Создаем бота

logger = telebot.logger  # настраиваем вывод логов
telebot.logger.setLevel(logging.DEBUG)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """стартовое сообщение"""
    with Session(engine) as session:  # используем контекст сессии базы данных
        try:  # так как пользователь может существовать до этого, ловим исключение
            u = User(first_name=message.from_user.first_name, telegram_id=message.from_user.id)  # создаем пользователя
            session.add(u)  # добавляем в сессию
            session.commit()  # подтверждаем изменения
        except Exception as e:
            print(e)  # в случае исключения выведем его на экран
    bot.reply_to(message, "Howdy, how are you doing?")  # ответ бота пользователю


@bot.message_handler(func=lambda message: message.text.split()[0] == 'Пользователь')
def get_msg(message):
    """обрабатываем сообщение начинающееся со слова Пользователь
    (метод split возвращает список из строк, раздеоенных пробеломБ обращаемся к первому элементу) """
    user_id = int(message.text.split()[1])  # вторым словом идет id пользователя, берем его и преобразуем в int
    with Session(engine) as session:
        u = select(User).where(User.id == user_id)  # создаем запрос для поиска пользователя с запрошенным id
        user = session.scalars(u).one()  # получаем объект пользователя
        m = select(Messages).where(Messages.user == user).limit(1)
        # создаем запрос для последнего сообщения пользователя
        msg = session.scalars(m).one()  # создаем объект сообщения
    bot.reply_to(message, msg)  # отвечаем пользователю с чужим сообщением


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """отвечаем на все сообщения """
    with Session(engine) as session:
        u = select(User).where(User.telegram_id == message.from_user.id)  # создаем запрос на поиск этого пользователя
        user = session.scalars(u).one()  # создаем объект пользователя
        m = Messages(text=message.text, user=user)  # создаем объект сообщения из данных сообщения
        session.add(m)  # добавляем сообщение в базу данных
        session.commit()  # подтверждаем изменения
    markup = types.InlineKeyboardMarkup(row_width=1)  # создаем клавиатуру
    key1 = types.InlineKeyboardButton(text='show your previous message',
                                      callback_data='user_prev_msg')  # создаем кнопки клавиатуры
    key2 = types.InlineKeyboardButton(text='show  previous foreign message', callback_data='prev_msg')
    key3 = types.InlineKeyboardButton(text='show users message', callback_data='another_user')
    markup.add(key1, key2, key3)  # добавляем кнопки в клавиатуру
    bot.reply_to(message, message.text, reply_markup=markup)  # отвечаем пользователю


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    """ Обрабатываем нажатия на inline клавиатуру"""
    if call.data == 'user_prev_msg':  # для кнопки ваши сообщения
        with Session(engine) as session:
            u = select(User).where(User.telegram_id == call.from_user.id)  # запрос на поиск текущего пользователя
            user = session.scalars(u).one()  # выполнение запроса создание пользователя из него
            m = select(Messages).where(Messages.user == user).limit(1)
            # создание запроса для поиска сообщения пользователя
            msg = session.scalars(m).one()  # создание сообщения
        bot.send_message(call.message.chat.id, msg)  # ответ
    elif call.data == 'prev_msg':  # для предыдущего сообщения любого пользователя
        with Session(engine) as session:
            m = select(Messages).limit(1)  # запрос для считывания последнего сообщения в таблице
            msg = session.scalars(m).one()  # создание сообщения
        bot.send_message(call.message.chat.id, msg)  # ответ
    elif call.data == 'another_user':  # для выбора сообщения другого пользователя
        markup = types.ReplyKeyboardMarkup(row_width=1)  # создание markup клавиатуры
        with Session(engine) as session:
            m = select(User).limit(5)  # запрашиваем 5 последних пользователей
            markup.add(*[types.KeyboardButton(f'Пользователь {u.id}') for u in session.scalars(m)])
            # добавляем кнопки пользователей
            # генератор создает строки 'Пользователь {u.id}' для каждого пользователя, полученного из базы данных
            # для распаковки списка в последовательность, перед ним ставим *

        bot.send_message(call.message.chat.id, "Выбери пользователя:", reply_markup=markup)  # ответ


bot.infinity_polling()  # метод с вечным циклом, в котором крутится бот
