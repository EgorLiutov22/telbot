import os

import logging
import telebot
from telebot import types

from sqlalchemy.orm import Session
from sqlalchemy import select

from engine import engine
from models import User, Messages

TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    with Session(engine) as session:
        try:
            u = User(first_name=message.from_user.first_name, telegram_id=message.from_user.id)
            session.add(u)
            session.commit()
        except Exception as e:
            print(e)
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda message: message.text.split()[0] == 'Пользователь')
def get_msg(message):
    user_id = int(message.text.split()[1])
    with Session(engine) as session:
        u = select(User).where(User.id == user_id)
        user = session.scalars(u).one()
        m = select(Messages).where(Messages.user == user).limit(1)
        msg = session.scalars(m).one()
    bot.reply_to(message, msg)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    with Session(engine) as session:
        u = select(User).where(User.telegram_id == message.from_user.id)
        user = session.scalars(u).one()
        # u = User(first_name=message.first_name, telegram_id=message.id)
        m = Messages(text=message.text, user=user)
        session.add(m)
        session.commit()
    key1 = types.InlineKeyboardButton(text='show your previous message', callback_data='user_prev_msg')
    key2 = types.InlineKeyboardButton(text='show  previous foreign message', callback_data='prev_msg')
    key3 = types.InlineKeyboardButton(text='show users message', callback_data='another_user')
    markup.add(key1, key2, key3)
    bot.reply_to(message, message.text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'user_prev_msg':
        with Session(engine) as session:
            u = select(User).where(User.telegram_id == call.from_user.id)
            user = session.scalars(u).one()
            m = select(Messages).where(Messages.user == user).limit(1)
            msg = session.scalars(m).one()
        bot.send_message(call.message.chat.id, msg)
    elif call.data == 'prev_msg':
        with Session(engine) as session:
            m = select(Messages).limit(1)
            msg = session.scalars(m).one()
        bot.send_message(call.message.chat.id, msg)
    elif call.data == 'another_user':
        markup = types.ReplyKeyboardMarkup(row_width=1)
        with Session(engine) as session:
            m = select(User).limit(5)
            markup.add(*[types.KeyboardButton(f'Пользователь {u.id}') for u in session.scalars(m)])

        bot.send_message(call.message.chat.id, "Выбери пользователя:", reply_markup=markup)


bot.infinity_polling()
