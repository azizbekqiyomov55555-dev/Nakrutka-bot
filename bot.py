import logging
import sqlite3
import asyncio
import secrets
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# --- SOZLAMALAR ---
API_TOKEN = '8066717720:AAEe3NoBcug1rTFT428HEBmJriwiutyWtr8'

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=API_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

# --- BAZANI SOZLASH ---
def init_db():
    conn = sqlite3.connect("sale_seen.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, 
        balance INTEGER DEFAULT 0,
        api_key TEXT
    )""")
    conn.commit()
    conn.close()

init_db()

# --- ASOSIY REPLAY MENYU ---
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🛍 Xizmatlar"), types.KeyboardButton(text="📲 Nomer olish"))
    builder.row(types.KeyboardButton(text="🛒 Buyurtmalarim"), types.KeyboardButton(text="👥 Pul ishlash"))
    builder.row(types.KeyboardButton(text="💵 Hisobim"), types.KeyboardButton(text="💰 Hisob To'ldirish"))
    builder.row(types.KeyboardButton(text="📞 Murojaat"), types.KeyboardButton(text="☎️ Qo'llab-quvvatlash"))
    builder.row(types.KeyboardButton(text="🤝 Hamkorlik"))
    return builder.as_markup(resize_keyboard=True)

# --- START ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("sale_seen.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        new_key = secrets.token_hex(16)
        cursor.execute("INSERT INTO users (id, api_key) VALUES (?, ?)", (user_id, new_key))
        conn.commit()
    conn.close()
    
    welcome_text = (
        f"👋 <b>Assalomu alaykum! {message.from_user.first_name}</b>\n\n"
        f"💙 @SaleSeenBot ga xush kelibsiz!\n\n"
        f"Ushbu bot orqali siz barcha platformalarga sifatli <b>NAKRUTKA</b> va "
        f"boshqa xizmatlardan foydalanishingiz mumkin."
    )
    await message.answer(welcome_text, reply_markup=main_menu())

# --- NOMER OLISH BO'LIMI (SIZ SO'RAGAN QISM) ---
@dp.message(F.text == "📲 Nomer olish")
async def get_number_section(message: types.Message):
    builder = InlineKeyboardBuilder()
    # Rasmga mos kategoriyalar
    builder.row(types.InlineKeyboardButton(text="🔹 Telegram", callback_data="num_tg"))
    builder.row(types.InlineKeyboardButton(text="🔸 Instagram", callback_data="num_inst"))
    builder.row(types.InlineKeyboardButton(text="🎬 TikTok", callback_data="num_tt"))
    builder.row(types.InlineKeyboardButton(text="🔴 YouTube", callback_data="num_yt"))
    builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main"))
    builder.adjust(2, 2, 1)

    text = (
        "📲 <b>Virtual nomerlar bo'limi</b>\n\n"
        "Siz ushbu bo'lim orqali ijtimoiy tarmoqlar uchun virtual nomerlarni "
        "avtomatik tarzda sotib olishingiz mumkin.\n\n"
        "📋 <b>Kerakli tarmoqni tanlang:</b>"
    )
    await message.answer(text, reply_markup=builder.as_markup())

# --- HAMKORLIK BO'LIMI ---
@dp.message(F.text == "🤝 Hamkorlik")
async def collab_main(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔥 SMM Panel API", callback_data="collab_smm"))
    builder.row(types.InlineKeyboardButton(text="☎️ TG Nomer API", callback_data="collab_nomer"))
    builder.row(types.InlineKeyboardButton(text="🤖 SMM Bot Yaratish", callback_data="collab_bot"))
    builder.adjust(1)
    
    text = (
        "🤝 <b>Hamkorlik dasturi. Biz bilan yangi daromad manbaingizni yarating.</b>\n\n"
        "<i>Tushunmasangiz:</i> @SaleContact murojaat qilishingiz mumkin.\n\n"
        "📋 <b>Kerakli bo'limni tanlang:</b>"
    )
    await message.answer(text, reply_markup=builder.as_markup())

# --- CALLBACK HANDLERLAR (SMM Panel va API qismlari) ---
@dp.callback_query(F.data == "collab_smm")
async def smm_panel(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔑 API Kalit", callback_data="show_api"))
    builder.row(types.InlineKeyboardButton(text="💼 Qo'llanmalar", callback_data="guides"))
    builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_collab"))
    
    text = "🔥 <b>SMM Panel - tizimi</b>\n\n📋 Ushbu tizim orqali siz SMM xizmatlariga API orqali buyurtma qilishingiz mumkin"
    await call.message.edit_text(text, reply_markup=builder.as_markup())

@dp.callback_query(F.data.in_({"show_api", "refresh_api"}))
async def api_key_page(call: types.CallbackQuery):
    user_id = call.from_user.id
    conn = sqlite3.connect("sale_seen.db")
    cursor = conn.cursor()
    
    if call.data == "refresh_api":
        new_key = secrets.token_hex(16)
        cursor.execute("UPDATE users SET api_key = ? WHERE id = ?", (new_key, user_id))
        conn.commit()
    
    cursor.execute("SELECT api_key FROM users WHERE id = ?", (user_id,))
    api_key = cursor.fetchone()[0]
    conn.close()
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="♻️ API kalitni yangilash", callback_data="refresh_api"))
    builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="collab_smm"))
    
    text = (
        f"📌 <b>Sizning API Manzilingiz</b> 👇:\n<code>https://saleseen.uz/api/v2</code>\n\n"
        f"📋 <b>Sizning API kalitingiz</b> 👇:\n<code>{api_key}</code>"
    )
    await call.message.edit_text(text, reply_markup=builder.as_markup())

@dp.callback_query(F.data == "back_to_collab")
async def back_to_collab_handler(call: types.CallbackQuery):
    await collab_main(call.message)
    await call.answer()

@dp.callback_query(F.data == "back_to_main")
async def back_to_main_handler(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("Asosiy menyuga qaytdingiz.", reply_markup=main_menu())

# --- QOLGAN TUGMALAR ---
@dp.message(F.text == "💵 Hisobim")
async def profile(message: types.Message):
    conn = sqlite3.connect("sale_seen.db")
    res = conn.execute("SELECT balance FROM users WHERE id = ?", (message.from_user.id,)).fetchone()
    conn.close()
    await message.answer(f"💰 Sizning balansingiz: <b>{res[0]} so'm</b>")

# --- ISHGA TUSHIRISH ---
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi")
    
