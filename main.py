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
    key1 = types.InlineKeyboardButton(text='show your previous message', callback_data='btn1')
    key2 = types.InlineKeyboardButton(text='show  previous foreign message', callback_data='btn2')
    markup.add(key1, key2)
    bot.reply_to(message, message.text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'btn1':
        with Session(engine) as session:
            u = select(User).where(User.telegram_id == call.message.from_user.id)
            m = select(Messages).where(Messages.user == u).limit(1)
        bot.send_message(call.message.chat.id, m[-1])
    elif call.data == 'btn2':
        with Session(engine) as session:
            m = select(Messages).limit(1)
        bot.send_message(call.message.chat.id, m[0])


bot.infinity_polling()
