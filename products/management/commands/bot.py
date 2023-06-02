import telebot
from django.conf import settings
from telebot import types
bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "я pricehub")





@bot.message_handler(func=lambda message: True, content_types=['audio', 'photo', 'voice', 'video', 'document',
                                                               'text', 'location', 'contact', 'sticker'])


def default_command(message):
    bot.send_message(message.chat.id, "fuck you")


bot.polling(none_stop=True)
