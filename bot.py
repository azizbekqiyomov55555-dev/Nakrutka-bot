import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Ma'lumotlar
API_TOKEN = '8066717720:AAEe3NoBcug1rTFT428HEBmJriwiutyWtr8'
ADMIN_ID = 8537782289

# Logging
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- KLAVIATURALAR ---

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🛍 Xizmatlar"), KeyboardButton("📲 Nomer olish"),
        KeyboardButton("🛒 Buyurtmalarim"), KeyboardButton("👥 Pul ishlash"),
        KeyboardButton("💰 Hisobim"), KeyboardButton("💰 Hisob To'ldirish"),
        KeyboardButton("📩 Murojaat"), KeyboardButton("☎️ Qo'llab-quvvatlash")
    )
    markup.row(KeyboardButton("🤝 Hamkorlik"))
    return markup

def admin_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📊 Statistika", callback_data="stats"),
        InlineKeyboardButton("📢 Reklama yuborish", callback_data="broadcast"),
        InlineKeyboardButton("➕ Pul qo'shish (User ID orqali)", callback_data="add_money")
    )
    return markup

# --- HANDLERLAR ---

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"👋 Assalomu alaykum! {user_name}\n\n"
        f"🤖 @SaleSeenBot nusxasiga xush kelibsiz!\n"
        f"Ushbu bot orqali barcha ijtimoiy tarmoqlarga sifatli NAKRUTKA "
        f"va virtual raqamlar olishingiz mumkin."
    )
    await message.answer(welcome_text, reply_markup=main_menu())

@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.from_id == ADMIN_ID:
        await message.answer("🛠 Admin panelga xush kelibsiz:", reply_markup=admin_menu())
    else:
        await message.answer("❌ Siz admin emassiz!")

@dp.message_handler(lambda message: message.text == "💰 Hisobim")
async def my_account(message: types.Message):
    text = (
        f"🗂 Kabinetingizga xush kelibsiz.\n\n"
        f"🆔 ID raqam: {message.from_id}\n"
        f"💵 Hisobingiz: 0 so'm\n"
        f"✅ Kiritgan pullaringiz: 0 so'm"
    )
    await message.answer(text)

@dp.message_handler(lambda message: message.text == "📲 Nomer olish")
async def get_number(message: types.Message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Bangladesh 🇧🇩 - 8958 so'm", callback_data="buy_bd"),
        InlineKeyboardButton("Hindiston 🇮🇳 - 11197 so'm", callback_data="buy_in")
    )
    await message.answer("👇 Kerakli davlatni tanlang:", reply_markup=markup)

@dp.message_handler(lambda message: message.text == "🤝 Hamkorlik")
async def partnership(message: types.Message):
    text = "🤝 Hamkorlik dasturi. Biz bilan yangi daromad manbaingizni yarating."
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🔥 SMM Panel API", callback_data="smm_api"),
        InlineKeyboardButton("☎️ TG Nomer API", callback_data="num_api")
    )
    await message.answer(text, reply_markup=markup)

# --- BOTNI ISHGA TUSHIRISH ---
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    
