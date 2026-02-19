import logging
import sqlite3
import asyncio
import secrets
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# --- SOZLAMALAR ---
API_TOKEN = '8066717720:AAEe3NoBcug1rTFT428HEBmJriwiutyWtr8'
ADMIN_ID = 8537782289 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# --- HOLATLAR ---
class OrderState(StatesGroup):
    waiting_for_quantity = State()
    waiting_for_link = State()

class AdminStates(StatesGroup):
    waiting_for_smm_url = State()
    waiting_for_smm_key = State()
    waiting_for_num_url = State()
    waiting_for_num_key = State()

# --- BAZA ---
def init_db():
    conn = sqlite3.connect("sale_seen.db")
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, api_key TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    conn.commit()
    conn.close()

init_db()

def get_db(): return sqlite3.connect("sale_seen.db")

def get_setting(key):
    with get_db() as conn:
        res = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return res[0] if res else None

# --- ADMIN PANEL ---
@dp.message(Command("admin"), F.from_user.id == ADMIN_ID)
async def admin_panel(message: types.Message):
    builder = InlineKeyboardBuilder()
    # SMM API tugmalari
    builder.row(types.InlineKeyboardButton(text="🛒 SMM API URL", callback_data="set_smm_url"),
                types.InlineKeyboardButton(text="🔑 SMM API KEY", callback_data="set_smm_key"))
    # Nomer API tugmalari
    builder.row(types.InlineKeyboardButton(text="📲 Nomer API URL", callback_data="set_num_url"),
                types.InlineKeyboardButton(text="🔑 Nomer API KEY", callback_data="set_num_key"))
    
    status = f"""🛠 <b>Admin Panel</b>
    
SMM URL: <code>{get_setting('smm_url')}</code>
Nomer URL: <code>{get_setting('num_url')}</code>"""
    
    await message.answer(status, reply_markup=builder.as_markup())

# --- ADMIN INPUT HANDLING (SMM & NOMER) ---
@dp.callback_query(F.data.startswith("set_"))
async def admin_set_api(call: types.CallbackQuery, state: FSMContext):
    target = call.data
    await call.message.answer(f"✍️ Ma'lumotni yuboring ({target}):")
    if target == "set_smm_url": await state.set_state(AdminStates.waiting_for_smm_url)
    elif target == "set_smm_key": await state.set_state(AdminStates.waiting_for_smm_key)
    elif target == "set_num_url": await state.set_state(AdminStates.waiting_for_num_url)
    elif target == "set_num_key": await state.set_state(AdminStates.waiting_for_num_key)

@dp.message(AdminStates.waiting_for_smm_url)
async def save_smm_url(message: types.Message, state: FSMContext):
    with get_db() as conn: conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('smm_url', ?)", (message.text,))
    await message.answer("✅ SMM URL saqlandi!"); await state.clear()

@dp.message(AdminStates.waiting_for_num_url)
async def save_num_url(message: types.Message, state: FSMContext):
    with get_db() as conn: conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('num_url', ?)", (message.text,))
    await message.answer("✅ Nomer API URL saqlandi!"); await state.clear()

@dp.message(AdminStates.waiting_for_smm_key)
async def save_smm_key(message: types.Message, state: FSMContext):
    with get_db() as conn: conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('smm_key', ?)", (message.text,))
    await message.answer("✅ SMM KEY saqlandi!"); await state.clear()

@dp.message(AdminStates.waiting_for_num_key)
async def save_num_key(message: types.Message, state: FSMContext):
    with get_db() as conn: conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('num_key', ?)", (message.text,))
    await message.answer("✅ Nomer KEY saqlandi!"); await state.clear()

# --- XIZMATLARNI API DAN YUKLASH ---
@dp.message(F.text == "🛍 Xizmatlar")
async def show_cats(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔵 Telegram", callback_data="list_Telegram"),
                types.InlineKeyboardButton(text="🟣 Instagram", callback_data="list_Instagram"))
    builder.row(types.InlineKeyboardButton(text="🛒 Barcha xizmatlar", callback_data="list_all"))
    await message.answer("✅ Tarmoqni tanlang:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("list_"))
async def list_services(call: types.CallbackQuery):
    cat = call.data.split("_")[1]
    url = get_setting("smm_url")
    key = get_setting("smm_key")
    
    if not url or not key: return await call.answer("❌ Admin SMM API ni sozlamagan!", show_alert=True)

    await call.answer("Xizmatlar yuklanmoqda...")
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data={'key': key, 'action': 'services'}) as resp:
            services = await resp.json()
            builder = InlineKeyboardBuilder()
            for s in services:
                if cat == "all" or cat.lower() in s['name'].lower() or cat.lower() in s.get('category','').lower():
                    builder.row(types.InlineKeyboardButton(text=f"{s['name']} - {s['rate']} so'm", 
                                                         callback_data=f"buy_{s['service']}_{s['min']}_{s['max']}"))
            
            builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_cats"))
            await call.message.edit_text(f"🛍 <b>{cat} xizmatlari:</b>", reply_markup=builder.as_markup())

# --- BUYURTMA (MIQDOR VA LINK) ---
@dp.callback_query(F.data.startswith("buy_"))
async def start_order(call: types.CallbackQuery, state: FSMContext):
    d = call.data.split("_")
    await state.update_data(s_id=d[1], min_q=d[2], max_q=d[3])
    await call.message.answer(f"🔢 <b>Miqdorni kiriting:</b>\n(Min: {d[2]} - Max: {d[3]})")
    await state.set_state(OrderState.waiting_for_quantity)

@dp.message(OrderState.waiting_for_quantity)
async def get_qty(message: types.Message, state: FSMContext):
    if not message.text.isdigit(): return await message.answer("Faqat raqam!")
    await state.update_data(qty=message.text)
    await message.answer("🔗 <b>Manzilni (Link) yuboring:</b>")
    await state.set_state(OrderState.waiting_for_link)

@dp.message(OrderState.waiting_for_link)
async def get_link(message: types.Message, state: FSMContext):
    data = await state.get_data()
    # API buyurtma yuborish kodi shu yerda bo'ladi
    await message.answer(f"✅ Buyurtma qabul qilindi!\nID: {data['s_id']}\nMiqdor: {data['qty']}\nLink: {message.text}")
    await state.clear()

# --- MENYU TUGMALARI ---
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🛍 Xizmatlar"), types.KeyboardButton(text="📲 Nomer olish"))
    builder.row(types.KeyboardButton(text="🤝 Hamkorlik"))
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Asosiy menyu", reply_markup=main_menu())

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    
