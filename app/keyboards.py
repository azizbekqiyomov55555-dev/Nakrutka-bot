from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🎮 Coin Flip"))
    kb.add(KeyboardButton("👤 Profil"))
    return kb
