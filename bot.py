import asyncio
import logging
import sqlite3
import random
import string
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import LabeledPrice, PreCheckoutQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# --- SOZLAMALAR ---
API_TOKEN = '8066717720:AAEe3NoBcug1rTFT428HEBmJriwiutyWtr8'
ADMIN_ID = 8537782289
CLICK_TOKEN = 'SIZNING_CLICK_TOKENINGIZ' # BotFather-dan olingan token

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- MA'LUMOTLAR BAZASI (SQLite) ---
db = sqlite3.connect("bot_users.db")
cursor = db.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0,
        total_in INTEGER DEFAULT 0,
        api_key TEXT
    )
""")
db.commit()

class PaymentState(StatesGroup):
    waiting_for_amount = State()

# --- YORDAMCHI FUNKSIYALAR ---
def get_user(user_id):
    cursor.execute("SELECT balance, total_in, api_key FROM users WHERE id = ?", (user_id,))
    res = cursor.fetchone()
    if not res:
        key = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
        cursor.execute("INSERT INTO users VALUES (?, 0, 0, ?)", (user_id, key))
        db.commit()
        return (0, 0, key)
    return res

# --- ASOSIY MENYU ---
def main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛍 Xizmatlar"), KeyboardButton(text="📲 Nomer olish")],
        [KeyboardButton(text="🛒 Buyurtmalarim"), KeyboardButton(text="👥 Pul ishlash")],
        [KeyboardButton(text="💰 Hisobim"), KeyboardButton(text="💰 Hisob To'ldirish")],
        [KeyboardButton(text="📩 Murojaat"), KeyboardButton(text="🤝 Hamkorlik")]
    ], resize_keyboard=True)

# --- START ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    get_user(message.from_user.id) # Bazaga qo'shish
    text = f"👋 Assalomu alaykum! {message.from_user.first_name}\n\n🟦 @SaleSeenBot ga xush kelibsiz!"
    await message.answer(text, reply_markup=main_menu())

# --- HISOBIM (7-RASM) ---
@dp.message(F.text == "💰 Hisobim")
async def my_account(message: types.Message):
    balance, total_in, _ = get_user(message.from_user.id)
    text = (
        "🏰 Kabinetingizga xush kelibsiz.\n\n"
        f"🆔 ID raqam: {message.from_user.id}\n"
        f"💵 Hisobingiz: {balance:,} so'm\n"
        f"✅ Kiritgan pullaringiz: {total_in:,} so'm"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Hisob To'ldirish", callback_data="p4")]
    ])
    await message.answer(text, reply_markup=kb)

# --- CLICK TO'LOV BOSHQARUVI ---
@dp.message(F.text == "💰 Hisob To'ldirish")
async def pay_init(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔵 CLICK Up [ Avto ]", callback_data="p4")]
    ])
    await message.answer("💰 To'lov tizimini tanlang:", reply_markup=kb)

@dp.callback_query(F.data == "p4")
async def click_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("💸 To'lov summasini kiriting (faqat raqam):")
    await state.set_state(PaymentState.waiting_for_amount)

@dp.message(PaymentState.waiting_for_amount)
async def send_invoice(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("❌ Faqat raqam yuboring!")
    
    amount = int(message.text)
    await state.clear()
    
    await message.answer_invoice(
        title="Balansni to'ldirish",
        description=f"Hisobga {amount:,} so'm qo'shish",
        provider_token=CLICK_TOKEN,
        currency="UZS",
        prices=[LabeledPrice(label="To'lov", amount=amount * 100)],
        payload=f"topup_{message.from_user.id}"
    )

@dp.pre_checkout_query()
async def checkout_check(query: PreCheckoutQuery):
    await query.answer(ok=True)

@dp.message(F.successful_payment)
async def pay_done(message: types.Message):
    amount = message.successful_payment.total_amount // 100
    user_id = message.from_user.id
    
    # BAZANI YANGILASH
    cursor.execute("UPDATE users SET balance = balance + ?, total_in = total_in + ? WHERE id = ?", (amount, amount, user_id))
    db.commit()
    
    await message.answer(f"✅ Tabriklaymiz! Hisobingizga {amount:,} so'm qo'shildi.")

# --- BOTNI ISHGA TUSHIRISH ---
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    
