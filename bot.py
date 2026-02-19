import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Ma'lumotlar
API_TOKEN = '8066717720:AAEe3NoBcug1rTFT428HEBmJriwiutyWtr8'
ADMIN_ID = 8537782289

# Logging
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- KLAVIATURALAR ---

def main_menu():
    buttons = [
        [KeyboardButton(text="🛍 Xizmatlar"), KeyboardButton(text="📲 Nomer olish")],
        [KeyboardButton(text="🛒 Buyurtmalarim"), KeyboardButton(text="👥 Pul ishlash")],
        [KeyboardButton(text="💰 Hisobim"), KeyboardButton(text="💰 Hisob To'ldirish")],
        [KeyboardButton(text="📩 Murojaat"), KeyboardButton(text="☎️ Qo'llab-quvvatlash")],
        [KeyboardButton(text="🤝 Hamkorlik")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def admin_menu():
    buttons = [
        [InlineKeyboardButton(text="📊 Statistika", callback_data="stats")],
        [InlineKeyboardButton(text="📢 Reklama yuborish", callback_data="broadcast")],
        [InlineKeyboardButton(text="➕ Pul qo'shish", callback_data="add_money")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- HANDLERLAR ---

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    welcome_text = (
        f"👋 Assalomu alaykum! {message.from_user.first_name}\n\n"
        f"🤖 @SaleSeenBot nusxasiga xush kelibsiz!\n"
        f"Sifatli NAKRUTKA va virtual raqamlar xizmati."
    )
    await message.answer(welcome_text, reply_markup=main_menu())

@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🛠 Admin panelga xush kelibsiz:", reply_markup=admin_menu())
    else:
        await message.answer("❌ Siz admin emassiz!")

@dp.message(F.text == "💰 Hisobim")
async def my_account(message: types.Message):
    text = (
        f"🗂 Kabinetingizga xush kelibsiz.\n\n"
        f"🆔 ID raqam: {message.from_user.id}\n"
        f"💵 Hisobingiz: 0 so'm\n"
        f"✅ Kiritgan pullaringiz: 0 so'm"
    )
    await message.answer(text)

@dp.message(F.text == "📲 Nomer olish")
async def get_number(message: types.Message):
    buttons = [
        [InlineKeyboardButton(text="Bangladesh 🇧🇩 - 8958 so'm", callback_data="buy_bd")],
        [InlineKeyboardButton(text="Hindiston 🇮🇳 - 11197 so'm", callback_data="buy_in")]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("👇 Kerakli davlatni tanlang:", reply_markup=markup)

# --- BOTNI ISHGA TUSHIRISH ---
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi")
        
