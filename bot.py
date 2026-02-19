import logging
import sqlite3
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from aiogram.utils import executor

# --- 1. SOZLAMALAR ---
API_TOKEN = '8066717720:AAEe3NoBcug1rTFT428HEBmJriwiutyWtr8'
ADMIN_ID = 8537782289  # O'zingizning ID raqamingizni yozing
PANEL_API_KEY = 'aee8149aa4fe37368499c64f63193153'
PANEL_URL = 'https://saleseen.uz/api/v2'
KARTA_RAQAM = "860006929870872"

# Bot va Logging
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# --- 2. MA'LUMOTLAR BAZASI (SQLite) ---
def init_db():
    conn = sqlite3.connect("bot_base.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = sqlite3.connect("bot_base.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else 0

def update_balance(user_id, amount):
    conn = sqlite3.connect("bot_base.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

# --- 3. KLAVIATURALAR ---
def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🚀 Buyurtma berish", callback_data="order_start"),
        InlineKeyboardButton("💰 Balans", callback_data="check_balance"),
        InlineKeyboardButton("💳 Hisobni to'ldirish", callback_data="fill_balance"),
        InlineKeyboardButton("🆘 Yordam", callback_data="help_info")
    )
    return kb

# --- 4. ASOSIY HANDLERLAR ---
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("bot_base.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()
    
    await message.answer(f"👋 Salom {message.from_user.first_name}!\nNakrutka botiga xush kelibsiz.", 
                         reply_markup=main_menu())

@dp.callback_query_handler(lambda c: c.data == 'check_balance')
async def balance_cb(callback_query: types.CallbackQuery):
    balance = get_balance(callback_query.from_user.id)
    await bot.send_message(callback_query.from_user.id, f"💵 Sizning balansingiz: **{balance} so'm**", parse_mode=ParseMode.MARKDOWN)

@dp.callback_query_handler(lambda c: c.data == 'fill_balance')
async def fill_cb(callback_query: types.CallbackQuery):
    text = (f"💳 **To'lov ma'lumotlari:**\n\n"
            f"Karta: `{KARTA_RAQAM}`\n"
            f"Ega: (Ismingiz)\n\n"
            f"Pulni o'tkazib, chekni (rasmni) shu yerga yuboring. Admin tasdiqlagach balansga tushadi.")
    await bot.send_message(callback_query.from_user.id, text, parse_mode=ParseMode.MARKDOWN)

# --- 5. ADMIN BUYRUQLARI ---
@dp.message_handler(commands=['pay'])
async def process_pay(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        try:
            parts = message.text.split()
            u_id, amount = int(parts[1]), int(parts[2])
            update_balance(u_id, amount)
            await message.answer(f"✅ ID {u_id} balansiga {amount} so'm qo'shildi.")
            await bot.send_message(u_id, f"✅ Hisobingiz {amount} so'mga to'ldirildi!")
        except:
            await message.answer("Xato! Namuna: `/pay ID SUMMA`")

@dp.message_handler(content_types=['photo'])
async def handle_receipt(message: types.Message):
    user_id = message.from_user.id
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, 
                         caption=f"🔔 **Yangi to'lov cheki!**\nID: `{user_id}`\n\nBalans qo'shish: `/pay {user_id} 10000`",
                         parse_mode=ParseMode.MARKDOWN)
    await message.answer("✅ Chek adminga yuborildi. Tekshiruvdan so'ng balans to'ldiriladi.")

# --- 6. BUYURTMA BERISH ---
@dp.callback_query_handler(lambda c: c.data == 'order_start')
async def order_info(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 
                           "🛒 Buyurtma berish uchun quyidagicha yozing:\n\n"
                           "`buyurtma XIZMAT_ID LINK MIQDOR`\n\n"
                           "Masalan: `buyurtma 1024 https://t.me/kanal 1000`", 
                           parse_mode=ParseMode.MARKDOWN)

@dp.message_handler(lambda message: message.text.startswith('buyurtma'))
async def make_order(message: types.Message):
    user_id = message.from_user.id
    balance = get_balance(user_id)
    
    # DIQQAT: Narxni hisoblashni panel API orqali yoki qo'lda qilishingiz kerak
    price = 5000 # Misol: 1000 ta obunachi 5000 so'm
    
    if balance < price:
        await message.answer("❌ Mablag' yetarli emas. Iltimos, hisobingizni to'ldiring.")
        return

    try:
        data = message.text.split()
        s_id, s_link, s_qty = data[1], data[2], data[3]
        
        # Panelga so'rov
        payload = {'key': PANEL_API_KEY, 'action': 'add', 'service': s_id, 'link': s_link, 'quantity': s_qty}
        res = requests.post(PANEL_URL, data=payload).json()
        
        if 'order' in res:
            update_balance(user_id, -price)
            await message.answer(f"✅ Buyurtma qabul qilindi! ID: {res['order']}\nBalansdan {price} so'm yechildi.")
        else:
            await message.answer(f"❌ Xato: {res.get('error', 'Noma`lum xato')}")
    except:
        await message.answer("❌ Xato format. Namuna: `buyurtma 1024 link 1000`")

# --- 7. ISHGA TUSHIRISH ---
if __name__ == '__main__':
    init_db()
    executor.start_polling(dp, skip_updates=True)
    
