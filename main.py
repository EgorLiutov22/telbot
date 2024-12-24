import os

import logging
import telebot
from telebot import types

TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    key1 = types.InlineKeyboardButton(text='a', callback_data='btn1')
    key2 = types.InlineKeyboardButton(text='v', callback_data='btn2')
    markup.add(key1, key2)
    bot.reply_to(message, message.text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'btn1':
        bot.send_message(call.message.chat.id, 'нажата кнопка 1')
    elif call.data == 'btn2':
        bot.send_message(call.message.chat.id, 'нажата кнопка 2')


bot.infinity_polling()
