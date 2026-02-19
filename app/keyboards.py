from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎮 Coin Flip")],
            [KeyboardButton(text="👤 Profil")]
        ],
        resize_keyboard=True
    )
