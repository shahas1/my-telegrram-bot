import telebot

TOKEN = '7888247063:AAFWCsoWVzftTMUgCSlk-IE4_94OfZOLsaI'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Salom, men ishga tushdim!")

bot.polling()
