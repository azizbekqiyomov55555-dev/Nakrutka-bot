import logging
import sqlite3
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# --- SOZLAMALAR ---
API_TOKEN = '8066717720:AAEe3NoBcug1rTFT428HEBmJriwiutyWtr8' # @BotFather dan olingan
PAYME_TOKEN = 'SIZNING_PAYME_TOKENINGIZ' # @BotFather -> Payments bo'limidan
ADMIN_ID = 8537782289 # O'zingizning ID raqamingiz

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# --- BAZANI SOZLASH ---
def init_db():
    conn = sqlite3.connect("sale_seen.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, 
        balance INTEGER DEFAULT 0, 
        referals INTEGER DEFAULT 0,
        invited_by INTEGER
    )""")
    conn.commit()
    conn.close()

init_db()

# --- HOLATLAR ---
class AdminStates(StatesGroup):
    broadcast = State()
    add_money_id = State()
    add_money_amount = State()

# --- KLAVIATURALAR ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🛍 Xizmatlar", "📲 Nomer olish")
    markup.add("🛒 Buyurtmalarim", "👥 Pul ishlash")
    markup.add("💵 Hisobim", "💰 Hisob To'ldirish")
    markup.add("📞 Murojaat", "☎️ Qo'llab-quvvatlash")
    markup.row("🤝 Hamkorlik")
    return markup

def admin_kb():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("📊 Statistika", callback_data="adm_stats"),
        types.InlineKeyboardButton("📢 Xabar yuborish", callback_data="adm_send"),
        types.InlineKeyboardButton("➕ Pul qo'shish", callback_data="adm_add")
    )
    return kb

# --- START VA RO'YXATDAN O'TISH ---
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    args = message.get_args()
    
    conn = sqlite3.connect("sale_seen.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    user_exists = cursor.fetchone()
    
    if not user_exists:
        referrer = int(args) if args and args.isdigit() else None
        cursor.execute("INSERT INTO users (id, invited_by) VALUES (?, ?)", (user_id, referrer))
        if referrer:
            cursor.execute("UPDATE users SET referals = referals + 1, balance = balance + 500 WHERE id = ?", (referrer,))
            try:
                await bot.send_message(referrer, "✅ Sizda yangi referal! Balansingizga 500 so'm qo'shildi.")
            except: pass
        conn.commit()
    conn.close()

    text = (f"👋 <b>Assalomu alaykum! {message.from_user.first_name}</b>\n\n"
            f"🤖 @SaleSeenBot ga xush kelibsiz!\n\n"
            "Ushbu bot orqali ijtimoiy tarmoqlarga <b>NAKRUTKA</b> va boshqa xizmatlardan foydalanishingiz mumkin.")
    await message.answer(text, reply_markup=main_menu())

# --- ADMIN PANEL ---
@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🛠 Admin boshqaruv paneli:", reply_markup=admin_kb())

@dp.callback_query_handler(lambda c: c.data == "adm_stats")
async def adm_stats(call: types.CallbackQuery):
    conn = sqlite3.connect("sale_seen.db")
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    await call.message.answer(f"👥 Jami foydalanuvchilar: {count} ta")

# --- FOYDALANUVCHI TUGMALARI ---
@dp.message_handler(lambda m: m.text == "💵 Hisobim")
async def profile(message: types.Message):
    conn = sqlite3.connect("sale_seen.db")
    res = conn.execute("SELECT balance, referals FROM users WHERE id = ?", (message.from_user.id,)).fetchone()
    text = (f"👤 <b>Profilingiz:</b>\n\n🆔 ID: <code>{message.from_user.id}</code>\n"
            f"💰 Balans: <b>{res[0]} so'm</b>\n👥 Referallar: <b>{res[1]} ta</b>")
    await message.answer(text)

@dp.message_handler(lambda m: m.text == "👥 Pul ishlash")
async def earn(message: types.Message):
    bot_info = await bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
    await message.answer(f"🎁 <b>Do'stlarni taklif qilib pul ishlang!</b>\n\nHar bir do'stingiz uchun 500 so'm beriladi.\n\n🔗 Havolangiz:\n{link}")

@dp.message_handler(lambda m: m.text == "💰 Hisob To'ldirish")
async def top_up(message: types.Message):
    await message.answer("💳 <b>Qancha miqdorda to'ldirmoqchisiz?</b> (Masalan: 5000)\n\n<i>Hozircha faqat Payme tizimi orqali:</i>")
    # To'lov mantiqi shu yerda bot.send_invoice orqali ulanadi

@dp.message_handler(lambda m: m.text == "🛍 Xizmatlar")
async def services(message: types.Message):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🔵 Telegram Xizmatlari", callback_data="s_tg"),
        types.InlineKeyboardButton("🟣 Instagram Xizmatlari", callback_data="s_inst"),
        types.InlineKeyboardButton("⚫️ TikTok Xizmatlari", callback_data="s_tt")
    )
    await message.answer("👇 Kerakli yo'nalishni tanlang:", reply_markup=kb)

@dp.message_handler(lambda m: m.text == "🤝 Hamkorlik")
async def collab(message: types.Message):
    await message.answer("🤝 <b>Biz bilan hamkorlik qilish uchun:</b>\n\nAdmin: @Sizning_Usernamengiz")

@dp.message_handler(lambda m: m.text == "📞 Murojaat")
async def contact(message: types.Message):
    await message.answer("🆘 Savol va takliflaringizni yozib qoldiring:\n\nSupport: @Sizning_Usernamengiz")

@dp.message_handler(lambda m: m.text == "📲 Nomer olish")
async def get_num(message: types.Message):
    await message.answer("🌐 <b>Virtual nomerlar (SMS) bo'limi:</b>\n\nTez kunda ishga tushadi...")

@dp.message_handler(lambda m: m.text == "🛒 Buyurtmalarim")
async def orders(message: types.Message):
    await message.answer("🗂 Sizning oxirgi 10 ta buyurtmangiz:\n\n<i>Hozircha buyurtmalar mavjud emas.</i>")

@dp.message_handler(lambda m: m.text == "☎️ Qo'llab-quvvatlash")
async def support_bot(message: types.Message):
    await message.answer("🤖 Bot bo'yicha texnik yordam: @Sizning_Usernamengiz")

# --- BOTNI ISHGA TUSHIRISH ---
if __name__ == '__main__':
    print("Bot ishlamoqda...")
    executor.start_polling(dp, skip_updates=True)
    
