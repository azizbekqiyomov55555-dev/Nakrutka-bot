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
GUIDE_VIDEO_ID = "BAACAgIAAxkBAA..." # Bu yerga yuborgan videongiz ID-sini qo'yasiz

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# --- FSM (ADMIN PANEL UCHUN) ---
class AdminStates(StatesGroup):
    waiting_for_api_url = State()
    waiting_for_api_key = State()

# --- BAZANI KENGAYTIRISH ---
def init_db():
    conn = sqlite3.connect("sale_seen.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, 
        balance INTEGER DEFAULT 0,
        api_key TEXT)""")
    # API sozlamalari uchun jadval
    cursor.execute("""CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY, 
        value TEXT)""")
    conn.commit()
    conn.close()

init_db()

# --- ADMIN PANEL FUNKSIYALARI ---
@dp.message(Command("admin"), F.from_user.id == ADMIN_ID)
async def admin_panel(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⚙️ API Sozlash", callback_data="admin_set_api"))
    builder.row(types.InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"))
    await message.answer("🛠 <b>Admin Panel</b>\n\nBotingizni boshqarish uchun bo'limni tanlang:", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "admin_set_api", F.from_user.id == ADMIN_ID)
async def set_api_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("🔗 Xizmatlar olinadigan API URL manzilini yuboring:\n(Masalan: <code>https://sayt.uz/api/v2</code>)")
    await state.set_state(AdminStates.waiting_for_api_url)

@dp.message(AdminStates.waiting_for_api_url)
async def save_url(message: types.Message, state: FSMContext):
    conn = sqlite3.connect("sale_seen.db")
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('api_url', ?)", (message.text,))
    conn.commit()
    conn.close()
    await message.answer("✅ URL saqlandi. Endi o'sha saytdagi <b>API KEY</b> (kalit)ingizni yuboring:")
    await state.set_state(AdminStates.waiting_for_api_key)

@dp.message(AdminStates.waiting_for_api_key)
async def save_key(message: types.Message, state: FSMContext):
    conn = sqlite3.connect("sale_seen.db")
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('main_api_key', ?)", (message.text,))
    conn.commit()
    conn.close()
    await message.answer("🎉 API sozlamalari muvaffaqiyatli saqlandi! Endi bot xizmatlarni avtomatik yuklaydi.")
    await state.clear()

# --- XIZMATLARNI API ORQALI OLISH ---
async def fetch_services():
    conn = sqlite3.connect("sale_seen.db")
    cursor = conn.cursor()
    url = cursor.execute("SELECT value FROM settings WHERE key = 'api_url'").fetchone()
    key = cursor.execute("SELECT value FROM settings WHERE key = 'main_api_key'").fetchone()
    conn.close()

    if url and key:
        async with aiohttp.ClientSession() as session:
            payload = {'key': key[0], 'action': 'services'}
            async with session.post(url[0], data=payload) as resp:
                if resp.status == 200:
                    return await resp.json()
    return None

@dp.message(F.text == "🛍 Xizmatlar")
async def show_services(message: types.Message):
    services = await fetch_services()
    if not services:
        return await message.answer("❌ Xizmatlar topilmadi. Admin API sozlamalarini tekshirishi kerak.")
    
    builder = InlineKeyboardBuilder()
    # Dastlabki 10 ta xizmatni ko'rsatish (namuna uchun)
    for service in services[:10]:
        builder.row(types.InlineKeyboardButton(text=f"{service['name']} - {service['rate']} so'm", callback_data=f"ser_{service['service']}"))
    
    await message.answer("🛍 <b>Mavjud xizmatlar ro'yxati:</b>", reply_markup=builder.as_markup())

# --- QO'LLANMA (VIDEO BILAN) ---
@dp.callback_query(F.data.startswith("api_guide_"))
async def video_guide(call: types.CallbackQuery):
    # Agar GUIDE_VIDEO_ID bo'lsa video yuboradi, bo'lmasa matn
    try:
        await call.message.answer_video(
            video=GUIDE_VIDEO_ID,
            caption="🎥 <b>Hamkorlik bo'limidan foydalanish bo'yicha video qo'llanma.</b>\n\nAgar savollar bo'lsa @Azizku_2008 ga yozing."
        )
    except:
        await call.message.answer("⚠️ Video hali yuklanmagan. Tez orada qo'shiladi!")
    await call.answer()

# --- MAIN ---
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    
