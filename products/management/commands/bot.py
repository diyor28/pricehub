import telebot
from django.conf import settings

from products.models import ProductModel


bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, f"Добро пожаловать в нашего бота PriceHub!\n\n"
                          "Мы рады видеть вас здесь.\n\n"
                          "Ищите товары по названию!")


@bot.message_handler(func=lambda message: True)
def default_search(message):
    search_title = message.text
    search_bot = ProductModel.objects.filter(title__icontains=search_title).order_by('price')[:5]

    if search_bot:
        bot.reply_to(message,f"Вот 7 самых дешевых продуктов по вашему запросу '{search_title}'")
        for n in search_bot:
            caption = f"Название: {n.title}\nЦена: {n.price:,}\nСсылка: {n.url}"
            bot.send_photo(message.chat.id, n.photo, caption)
    else:
        bot.reply_to(message, "Ничего не найдено,\n"
                              "попробуйте искать по ключевым словам!\n")

# @bot.message_handler(func=lambda message: True)
# def default_search2(message):
#     trip = 0
#     search_title2 = SearchQuery(message.text)
#     search_bot2 = ProductModel.objects.annotate(rank=SearchRank('index',(search_title2))).order_by('price')[:5]
#
#     print(search_bot2)
#     if search_bot2:
#         for n in search_bot2:
#             trip += 1
#             caption = f"Название: {n.title}\nЦена: {n.price:,}\nСсылка:{n.url}"
#
#             bot.send_photo(message.chat.id, n.photo, caption)
#
#             if trip == 5:
#                 break
#
#     else:
#         bot.reply_to(message, "Hе существует")
bot.polling(none_stop=True)

