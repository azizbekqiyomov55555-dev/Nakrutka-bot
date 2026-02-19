import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Bot tokeningizni shu yerga yozing (@BotFather dan olinadi)
API_TOKEN = '8066717720:AAEe3NoBcug1rTFT428HEBmJriwiutyWtr8'

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- Tugmalarni yaratish ---
def get_main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    buttons = [
        KeyboardButton("🛍 Xizmatlar"),
        KeyboardButton("📲 Nomer olish"),
        KeyboardButton("🛒 Buyurtmalarim"),
        KeyboardButton("🫂 Pul ishlash"),
        KeyboardButton("💵 Hisobim"),
        KeyboardButton("💰 Hisob To'ldirish"),
        KeyboardButton("📞 Murojaat"),
        KeyboardButton("☎️ Qo'llab-quvvatlash")
    ]
    
    keyboard.add(*buttons)
    keyboard.row(KeyboardButton("🤝 Hamkorlik"))
    return keyboard

# --- Komandalar ---
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"👋 Assalomu alaykum! {user_name}\n\n"
        f"🤖 @SaleSeenBot ga xush kelibsiz!\n\n"
        "Ushbu bot orqali siz barcha platformalarga sifatli va "
        "hamyonbob **NAKRUTKA** va boshqa xizmatlardan foydalanishingiz mumkin."
    )
    await message.answer(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

# --- Tugmalar uchun handlerlar ---
@dp.message_handler(lambda message: message.text == "🛍 Xizmatlar")
async def services(message: types.Message):
    await message.answer("Kategoriyani tanlang:\n1. Telegram\n2. Instagram\n3. TikTok")

@dp.message_handler(lambda message: message.text == "💵 Hisobim")
async def check_balance(message: types.Message):
    await message.answer("Sizning hisobingiz: 0 so'm")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
