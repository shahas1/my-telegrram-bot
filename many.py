import telebot
from telebot import types
import json
import os

# TOKEN
TOKEN = '7888247063:AAFWCsoWVzftTMUgCSlk-IE4_94OfZOLsaI'
bot = telebot.TeleBot(TOKEN)

# ADMIN PANEL KODI VA USERLAR
ADMIN_SECRET_CODE = '2010'
ADMIN_CHAT_ID = None  # Admin ID sessiyada saqlanadi

# MA'LUMOTLAR FAYLI
DATA_FILE = 'codes.json'

# JSONni yuklash
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

# JSONni saqlash
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# START
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Kod kiriting:")
    bot.register_next_step_handler(message, user_enter_code)

# USER KOD KIRITADI
def user_enter_code(message):
    data = load_data()
    code = message.text.strip()

    # ADMIN KODI
    if code == ADMIN_SECRET_CODE:
        global ADMIN_CHAT_ID
        ADMIN_CHAT_ID = message.chat.id
        admin_panel(message)
        return

    # ODDIY USER
    if code in data:
        markup = types.InlineKeyboardMarkup()
        for idx, part in enumerate(data[code]):
            markup.add(types.InlineKeyboardButton(f'Qism {idx + 1}', callback_data=f'showpart|{code}|{idx}'))
        bot.send_message(message.chat.id, f"\"{code}\" kodi bo'yicha qismlar:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Bunday kod topilmadi!")

# ADMIN PANELI
def admin_panel(message):
    data = load_data()
    markup = types.InlineKeyboardMarkup()

    for code in data:
        markup.add(types.InlineKeyboardButton(code, callback_data=f'admincode|{code}'))

    markup.add(types.InlineKeyboardButton("+ Yangi kod qo'shish", callback_data='addnewcode'))
    bot.send_message(message.chat.id, "Admin panelga xush kelibsiz!", reply_markup=markup)

# CALLBACK LAR
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = load_data()

    # FOYDALANUVCHI QISM KO'RISH
    if call.data.startswith('showpart'):
        _, code, idx = call.data.split('|')
        idx = int(idx)
        try:
            file_id = data[code][idx]
            bot.send_video(call.message.chat.id, file_id)
        except IndexError:
            bot.send_message(call.message.chat.id, "Qism topilmadi!")

    # ADMIN PANELI KOD USTIDA
    elif call.data.startswith('admincode'):
        _, code = call.data.split('|')

        markup = types.InlineKeyboardMarkup()
        for idx, part in enumerate(data[code]):
            markup.add(types.InlineKeyboardButton(f'Qism {idx + 1}', callback_data=f'showpart|{code}|{idx}'))

        markup.add(types.InlineKeyboardButton("+ Yangi qism qo'shish", callback_data=f'addpart|{code}'))
        markup.add(types.InlineKeyboardButton("Kod nomini o'zgartirish", callback_data=f'renamecode|{code}'))
        markup.add(types.InlineKeyboardButton("Kod o'chirish", callback_data=f'deletecode|{code}'))
        markup.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data='backadmin'))

        bot.edit_message_text(f"{code} kodi uchun amallar:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    # YANGI QISM QO'SHISH
    elif call.data.startswith('addpart'):
        _, code = call.data.split('|')
        msg = bot.send_message(call.message.chat.id, f"{code} kodi uchun yangi video yuboring:")
        bot.register_next_step_handler(msg, save_new_part, code)

    # YANGI KOD QO'SHISH
    elif call.data == 'addnewcode':
        msg = bot.send_message(call.message.chat.id, "Yangi kod nomini kiriting:")
        bot.register_next_step_handler(msg, create_new_code)

    # KOD NOMINI O'ZGARTIRISH
    elif call.data.startswith('renamecode'):
        _, code = call.data.split('|')
        msg = bot.send_message(call.message.chat.id, f"{code} kodini yangi nomga o'zgartiring:")
        bot.register_next_step_handler(msg, rename_code, code)

# KOD O'CHIRISH
    elif call.data.startswith('deletecode'):
        _, code = call.data.split('|')
        if code in data:
            del data[code]
            save_data(data)
            bot.send_message(call.message.chat.id, f"{code} kodi o'chirildi!")
            admin_panel(call.message)

    # ORTGA
    elif call.data == 'backadmin':
        admin_panel(call.message)

# YANGI QISMNI SAQLASH
def save_new_part(message, code):
    if not message.video:
        bot.send_message(message.chat.id, "Faqat video yuboring!")
        return
    data = load_data()
    file_id = message.video.file_id
    data[code].append(file_id)
    save_data(data)
    bot.send_message(message.chat.id, f"{code} kodi uchun yangi video qism qo'shildi!")
    admin_panel(message)

# YANGI KOD YARATISH
def create_new_code(message):
    data = load_data()
    code = message.text.strip()

    if code in data:
        bot.send_message(message.chat.id, "Bu kod allaqachon mavjud!")
        admin_panel(message)
        return

    data[code] = []
    save_data(data)
    bot.send_message(message.chat.id, f"{code} kodi yaratildi!")
    admin_panel(message)

# KOD NOMINI O'ZGARTIRISH
def rename_code(message, old_code):
    data = load_data()
    new_code = message.text.strip()

    if new_code in data:
        bot.send_message(message.chat.id, "Bu kod allaqachon mavjud!")
        admin_panel(message)
        return

    data[new_code] = data.pop(old_code)
    save_data(data)
    bot.send_message(message.chat.id, f"{old_code} kod nomi {new_code} ga o'zgartirildi!")
    admin_panel(message)

# BOT POLLING
print("Bot ishga tushdi...")
bot.polling(none_stop=True)
