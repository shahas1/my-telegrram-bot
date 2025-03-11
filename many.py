import telebot
from telebot import types

# Bot tokeni
TOKEN = '7888247063:AAFWCsoWVzftTMUgCSlk-IE4_94OfZOLsaI'
bot = telebot.TeleBot(TOKEN)

# Admin username va maxfiy kod
ADMIN_USERNAME = "@SAKUROM"
SECRET_ADMIN_CODE = "2010"  # Maxfiy admin kodi

# Kodlar va qismlar (misol uchun)
codes_data = {
    '1234': {
        'anime_name': 'Naruto',
        'episodes': {
            1: 'https://link-episode-1',
            2: 'https://link-episode-2'
        }
    }
}

# Start komandasi
@bot.message_handler(commands=['start'])
def start_handler(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔑 Kod kiritish", "👤 Adminga murojaat")
    bot.send_message(chat_id, "Xush kelibsiz!\n\nKerakli bo'limni tanlang.", reply_markup=markup)

# Tugmalar
@bot.message_handler(func=lambda message: True)
def message_handler(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if text == "🔑 Kod kiritish":
        bot.send_message(chat_id, "Kod kiriting:")
        bot.register_next_step_handler(message, kod_kiritish)

    elif text == "👤 Adminga murojaat":
        bot.send_message(chat_id, f"Admin: {ADMIN_USERNAME}")

    elif text == "/shah":
        bot.send_message(chat_id, "Maxfiy kodni kiriting:")
        bot.register_next_step_handler(message, check_admin_code)

# Kod tekshirish
def kod_kiritish(message):
    chat_id = message.chat.id
    code = message.text.strip()

    if code in codes_data:
        anime = codes_data[code]
        markup = types.InlineKeyboardMarkup()

        for ep_num in anime['episodes']:
            btn = types.InlineKeyboardButton(f"{ep_num}-qism", callback_data=f"{code}|{ep_num}")
            markup.add(btn)

        bot.send_message(chat_id, f"{anime['anime_name']} qismlari:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Kod noto'g'ri!")

# Inline tugmalar uchun
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    data = call.data.split('|')
    code = data[0]
    ep_num = int(data[1])

    if code in codes_data:
        episode_link = codes_data[code]['episodes'].get(ep_num)
        if episode_link:
            bot.send_message(chat_id, f"{ep_num}-qism linki: {episode_link}")
        else:
            bot.send_message(chat_id, "Qism topilmadi!")

# Maxfiy admin panel
def check_admin_code(message):
    chat_id = message.chat.id
    code = message.text.strip()

    if code == SECRET_ADMIN_CODE:
        show_admin_panel(chat_id)
    else:
        bot.send_message(chat_id, "Maxfiy kod noto'g'ri!")

def show_admin_panel(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Kod qo'shish", "➕ Qism qo'shish", "⬅️ Ortga chiqish")
    bot.send_message(chat_id, "Admin paneliga xush kelibsiz!", reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(chat_id, admin_panel_actions)

def admin_panel_actions(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if text == "➕ Kod qo'shish":
        bot.send_message(chat_id, "Yangi kod kiriting:")
        bot.register_next_step_handler(message, add_new_code)

    elif text == "➕ Qism qo'shish":
        bot.send_message(chat_id, "Kod kiriting:")
        bot.register_next_step_handler(message, add_episode_code)

    elif text == "⬅️ Ortga chiqish":
        start_handler(message)

def add_new_code(message):
    chat_id = message.chat.id
    new_code = message.text.strip()

    if new_code in codes_data:
        bot.send_message(chat_id, "Bu kod allaqachon mavjud.")
    else:
        codes_data[new_code] = {'anime_name': '', 'episodes': {}}
        bot.send_message(chat_id, "Anime nomini kiriting:")
        bot.register_next_step_handler(message, lambda m: add_anime_name(m, new_code))

def add_anime_name(message, code):
    anime_name = message.text.strip()
    codes_data[code]['anime_name'] = anime_name
    bot.send_message(message.chat.id, f"Anime '{anime_name}' kod '{code}' bilan yaratildi!")

def add_episode_code(message):
    chat_id = message.chat.id
    code = message.text.strip()

    if code not in codes_data:
        bot.send_message(chat_id, "Bu kod topilmadi!")
    else:
        bot.send_message(chat_id, "Qism raqamini kiriting:")
        bot.register_next_step_handler(message, lambda m: add_episode_number(m, code))

def add_episode_number(message, code):
    try:
        ep_num = int(message.text.strip())
        bot.send_message(message.chat.id, "Qism linkini yuboring:")
        bot.register_next_step_handler(message, lambda m: add_episode_link(m, code, ep_num))
    except ValueError:
        bot.send_message(message.chat.id, "Faqat raqam kiriting!")

def add_episode_link(message, code, ep_num):
    link = message.text.strip()
    codes_data[code]['episodes'][ep_num] = link
    bot.send_message(message.chat.id, f"{ep_num}-qism linki qo'shildi!")

# Botni ishga tushirish
bot.polling(non_stop=True)
