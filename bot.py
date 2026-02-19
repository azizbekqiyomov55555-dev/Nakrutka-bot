import asyncio
import logging
import random
import string
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# --- SOZLAMALAR ---
API_TOKEN = '8066717720:AAEe3NoBcug1rTFT428HEBmJriwiutyWtr8'
ADMIN_ID = 8537782289

user_data = {}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- YORDAMCHI FUNKSIYALAR ---
def get_api_key(user_id):
    if user_id not in user_data:
        user_data[user_id] = {'key': ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))}
    return user_data[user_id]['key']

# --- KLAVIATURALAR ---
def main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛍 Xizmatlar"), KeyboardButton(text="📲 Nomer olish")],
        [KeyboardButton(text="🛒 Buyurtmalarim"), KeyboardButton(text="👥 Pul ishlash")],
        [KeyboardButton(text="💰 Hisobim"), KeyboardButton(text="💰 Hisob To'ldirish")],
        [KeyboardButton(text="📩 Murojaat"), KeyboardButton(text="☎️ Qo'llab-quvvatlash")],
        [KeyboardButton(text="🤝 Hamkorlik")]
    ], resize_keyboard=True)

# --- 1-RASM: START ---
@dp.message(Command("start"))
async def start_command(message: types.Message):
    text = (
        f"👋 Assalomu alaykum! {message.from_user.first_name}\n\n"
        f"🟦 @SaleSeenBot ga xush kelibsiz!\n\n"
        f"📊 Ushbu bot orqali siz barcha platformalarga shuningdek\n"
        f"🔵 Telegram, 🟣 Instagram, ⚫️ TikTok, 🔴 YouTube va boshqa tarmoqlarga "
        f"sifatli va hamyonbop **NAKRUTKA** va Boshqa xizmatlardan foydalanishingiz mumkin 🔵\n\n"
        f"🕹 Bot qo'llanmasi: /qollanma"
    )
    await message.answer(text, reply_markup=main_menu())

# --- 8-RASM: MUROJAAT ---
@dp.message(F.text == "📩 Murojaat")
async def murojaat(message: types.Message):
    text = "⭐ Bizga savollaringiz bormi?\n\n📄 Murojaat matnini yozib yuboring."
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Orqaga", callback_data="home")]])
    await message.answer(text, reply_markup=kb)

# --- 11-12-RASMLAR: SMM PANEL API ---
@dp.callback_query(F.data == "smm_api")
async def smm_api_handler(callback: types.CallbackQuery):
    text = (
        "🔥 SMM Panel API - tizimi\n\n"
        "📋 Ushbu bo'lim orqali siz botimizning SMM xizmatlarini "
        "o'z botingizga yoki saytingizga API orqali ulashingiz mumkin.\n\n"
        "🌐 API URL: `https://saleseen.uz/api/v2`"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 API Kalit", callback_data="get_key")],
        [InlineKeyboardButton(text="💼 Qo'llanmalar", url="https://saleseen.uz/api")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_ham")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")

# --- 14-15-RASMLAR: TG NOMER API ---
@dp.callback_query(F.data == "num_api")
async def num_api(callback: types.CallbackQuery):
    text = "☎️ Nomer API - tizimi\n\n📋 Ushbu tizim orqali siz Tayyor Akkauntlarga API olishingiz mumkin"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 API Kalit", callback_data="get_key")],
        [InlineKeyboardButton(text="💼 Qo'llanmalar", callback_data="guide")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_ham")]
    ])
    await callback.message.edit_text(text, reply_markup=kb)

# --- API KEY KO'RSATISH VA YANGILASH ---
@dp.callback_query(F.data == "get_key")
async def show_key(callback: types.CallbackQuery):
    key = get_api_key(callback.from_user.id)
    text = f"Api urllar va dokumentlar 💼 Qo'llanmalar bo'limida.\n\n📋 Sizning API kalitingiz 👇:\n\n`{key}`"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="♻️ API kalitni yangilash", callback_data="new_key")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_ham")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "new_key")
async def update_key(callback: types.CallbackQuery):
    user_data[callback.from_user.id]['key'] = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
    await callback.answer("✅ API kalit yangilandi!")
    await show_key(callback)

# --- HAMKORLIK ---
@dp.callback_query(F.data == "back_ham")
@dp.message(F.text == "🤝 Hamkorlik")
async def hamkorlik_main(message: types.Message | types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 SMM Panel API", callback_data="smm_api")],
        [InlineKeyboardButton(text="☎️ TG Nomer API", callback_data="num_api")],
        [InlineKeyboardButton(text="🤖 SMM Bot Yaratish", url="https://t.me/SaleContact")]
    ])
    text = "🤝 Hamkorlik dasturi. Biz bilan yangi daromad manbaingizni yarating.\n\nTushunmasangiz: @SaleContact murojaat qiling."
    
    if isinstance(message, types.Message):
        await message.answer(text, reply_markup=kb)
    else:
        await message.edit_text(text, reply_markup=kb)

# --- ASOSIY ISHGA TUSHIRISH ---
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    
