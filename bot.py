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
ADMIN_USERNAME = "@Azizku_2008"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

class AdminStates(StatesGroup):
    waiting_for_api_url = State()
    waiting_for_api_key = State()
    waiting_for_video = State()

# --- BAZA (SQLite) ---
def init_db():
    conn = sqlite3.connect("sale_seen.db")
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, api_key TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    conn.commit()
    conn.close()

init_db()

def get_db():
    return sqlite3.connect("sale_seen.db")

def get_setting(key):
    with get_db() as conn:
        res = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return res[0] if res else None

# --- REPLAY MENYULAR ---
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🛍 Xizmatlar"), types.KeyboardButton(text="📲 Nomer olish"))
    builder.row(types.KeyboardButton(text="🛒 Buyurtmalarim"), types.KeyboardButton(text="👥 Pul ishlash"))
    builder.row(types.KeyboardButton(text="💵 Hisobim"), types.KeyboardButton(text="💰 Hisob To'ldirish"))
    builder.row(types.KeyboardButton(text="📞 Murojaat"), types.KeyboardButton(text="☎️ Qo'llab-quvvatlash"))
    builder.row(types.KeyboardButton(text="🤝 Hamkorlik"))
    return builder.as_markup(resize_keyboard=True)

def nomer_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="📞 Telegram Akauntlar"), types.KeyboardButton(text="☎️ Boshqa Tarmoqlar"))
    builder.row(types.KeyboardButton(text="Bosh sahifa ⬆️"))
    return builder.as_markup(resize_keyboard=True)

# --- START ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            conn.execute("INSERT INTO users (id, api_key) VALUES (?, ?)", (user_id, secrets.token_hex(16)))
            conn.commit()
    await message.answer(f"👋 Assalomu alaykum! {message.from_user.first_name}\n\n🤖 @SaleSeenBot ga xush kelibsiz!", reply_markup=main_menu())

# --- 1. SMM XIZMATLAR (API BILAN ISHLASH) ---
@dp.message(F.text == "🛍 Xizmatlar")
async def smm_cats(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔵 Telegram", callback_data="fetch_Telegram"),
                types.InlineKeyboardButton(text="🟣 Instagram", callback_data="fetch_Instagram"))
    builder.row(types.InlineKeyboardButton(text="⚫️ TikTok", callback_data="fetch_TikTok"),
                types.InlineKeyboardButton(text="🔴 YouTube", callback_data="fetch_YouTube"))
    builder.row(types.InlineKeyboardButton(text="🔍 Qidirish", callback_data="search_ser"),
                types.InlineKeyboardButton(text="🎟 2-Bo'lim", callback_data="section_2"))
    builder.row(types.InlineKeyboardButton(text="🛒 Barcha xizmatlar", callback_data="fetch_all"))
    builder.row(types.InlineKeyboardButton(text="⏪ Orqaga", callback_data="back_home"))
    
    await message.answer("✅ <b>Ijtimoiy tarmoqlardan birini tanlang:</b>", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("fetch_"))
async def api_services_loader(call: types.CallbackQuery):
    cat_query = call.data.split("_")[1]
    url = get_setting("api_url")
    key = get_setting("main_api_key")
    
    if not url or not key:
        return await call.message.answer("❌ Admin tomonidan API sozlanmagan!")

    await call.answer("Yuklanmoqda...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, data={'key': key, 'action': 'services'}) as resp:
                data = await resp.json()
                builder = InlineKeyboardBuilder()
                found = 0
                for s in data:
                    if cat_query == "all" or cat_query.lower() in s['name'].lower() or cat_query.lower() in s.get('category','').lower():
                        builder.row(types.InlineKeyboardButton(text=f"{s['name']} - {s['rate']} so'm", callback_data=f"buy_{s['service']}"))
                        found += 1
                        if found >= 15: break
                
                if found == 0: await call.message.answer("Xizmat topilmadi.")
                else: 
                    builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_smm"))
                    await call.message.edit_text(f"🛍 <b>{cat_query} bo'yicha xizmatlar:</b>", reply_markup=builder.as_markup())
        except:
            await call.message.answer("⚠️ API xatolik yuz berdi.")

# --- 2. NOMER OLISH (TG AKAUNTLAR) ---
@dp.message(F.text == "📲 Nomer olish")
async def nomer_olish_start(message: types.Message):
    await message.answer("👇 Kerakli tarmoqni tanlang.", reply_markup=nomer_menu())

@dp.message(F.text == "📞 Telegram Akauntlar")
@dp.callback_query(F.data == "tg_page_1")
async def tg_p1(event):
    builder = InlineKeyboardBuilder()
    p1 = [("Bangladesh 🇧🇩 - 8958", "b"), ("Hindiston 🇮🇳 - 11197", "b"), ("Keniya 🇰🇪 - 11197", "b"), ("Kolumbiya 🇨🇴 - 12317", "b"), ("Azerbaijan 🇦🇿 - 13437", "b"), ("Dominikana 🇩🇴 - 13437", "b"), ("Shri Lanka 🇱🇰 - 14556", "b"), ("Marokash 🇲🇦 - 14556", "b")]
    for t, c in p1: builder.add(types.InlineKeyboardButton(text=t, callback_data=c))
    builder.adjust(2)
    builder.row(types.InlineKeyboardButton(text="🥷 Admin orqali nomer olish", url=f"https://t.me/{ADMIN_USERNAME.replace('@','') }"))
    builder.row(types.InlineKeyboardButton(text="1/9", callback_data="n"), types.InlineKeyboardButton(text="⏩ Keyingi", callback_data="tg_page_2"))
    
    txt = "📞 <b>Telegram akauntlar ro'yxati:</b>"
    if isinstance(event, types.Message): await event.answer(txt, reply_markup=builder.as_markup())
    else: await event.message.edit_text(txt, reply_markup=builder.as_markup())

@dp.callback_query(F.data == "tg_page_2")
async def tg_p2(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    p2 = [("AQSh 🇺🇸 - 16796", "b"), ("Afg'oniston 🇦🇫 - 16796", "b"), ("O'zbekiston 🇺🇿 - 17916", "b"), ("Braziliya 🇧🇷 - 19035", "b")]
    for t, c in p2: builder.add(types.InlineKeyboardButton(text=t, callback_data=c))
    builder.adjust(2)
    builder.row(types.InlineKeyboardButton(text="⏪ Oldingi", callback_data="tg_page_1"), types.InlineKeyboardButton(text="2/9", callback_data="n"))
    await call.message.edit_text("🛒 <b>2-sahifa:</b>", reply_markup=builder.as_markup())

# --- 3. HAMKORLIK ---
@dp.message(F.text == "🤝 Hamkorlik")
async def collab_menu(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔥 SMM Panel API", callback_data="s_smm"),
                types.InlineKeyboardButton(text="☎️ TG Nomer API", callback_data="s_num"))
    builder.row(types.InlineKeyboardButton(text="🤖 SMM Bot Yaratish", callback_data="s_bot"))
    builder.adjust(1)
    await message.answer("🤝 <b>Hamkorlik dasturi:</b>", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "s_smm")
async def s_smm_h(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔑 API Kalit", callback_data="my_api_key"),
                types.InlineKeyboardButton(text="💼 Qo'llanmalar", callback_data="v_guide"))
    builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_collab"))
    await call.message.edit_text("🔥 <b>SMM Panel API tizimi:</b>", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "my_api_key")
async def my_api_key(call: types.CallbackQuery):
    with get_db() as conn:
        u = conn.execute("SELECT api_key FROM users WHERE id = ?", (call.from_user.id,)).fetchone()
    txt = f"📌 <b>URL:</b> <code>https://saleseen.uz/api/v2</code>\n📋 <b>Key:</b> <code>{u[0]}</code>"
    builder = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="s_smm"))
    await call.message.edit_text(txt, reply_markup=builder.as_markup())

# --- 4. ADMIN PANEL ---
@dp.message(Command("admin"), F.from_user.id == ADMIN_ID)
async def admin_p(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔗 API URL", callback_data="a_url"),
                types.InlineKeyboardButton(text="🔑 API KEY", callback_data="a_key"))
    builder.row(types.InlineKeyboardButton(text="🎥 Video Yuklash", callback_data="a_vid"))
    await message.answer("🛠 <b>Admin Panel:</b>", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "a_url")
async def a_url(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("API URL yuboring:"); await state.set_state(AdminStates.waiting_for_api_url)

@dp.message(AdminStates.waiting_for_api_url)
async def s_url(message: types.Message, state: FSMContext):
    with get_db() as conn: conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('api_url', ?)", (message.text,))
    await message.answer("Saqlandi!"); await state.clear()

@dp.callback_query(F.data == "a_key")
async def a_key(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("API KEY yuboring:"); await state.set_state(AdminStates.waiting_for_api_key)

@dp.message(AdminStates.waiting_for_api_key)
async def s_key(message: types.Message, state: FSMContext):
    with get_db() as conn: conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('main_api_key', ?)", (message.text,))
    await message.answer("Saqlandi!"); await state.clear()

@dp.callback_query(F.data == "a_vid")
async def a_vid(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Videoni yuboring:"); await state.set_state(AdminStates.waiting_for_video)

@dp.message(AdminStates.waiting_for_video, F.video)
async def s_vid(message: types.Message, state: FSMContext):
    with get_db() as conn: conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('guide_video', ?)", (message.video.file_id,))
    await message.answer("Video saqlandi!"); await state.clear()

@dp.callback_query(F.data == "v_guide")
async def v_guide(call: types.CallbackQuery):
    v = get_setting("guide_video")
    if v: await call.message.answer_video(video=v, caption="🎥 Qo'llanma")
    else: await call.answer("Video yo'q", show_alert=True)

# --- NAVIGATSIYA ---
@dp.callback_query(F.data == "back_home")
async def bh(call: types.CallbackQuery): await call.message.answer("Menyu", reply_markup=main_menu())

@dp.callback_query(F.data == "back_to_smm")
async def bts(call: types.CallbackQuery): await smm_cats(call.message)

@dp.callback_query(F.data == "back_collab")
async def bc(call: types.CallbackQuery): await collab_menu(call.message)

@dp.message(F.text == "Bosh sahifa ⬆️")
async def bsh(message: types.Message): await message.answer("Asosiy", reply_markup=main_menu())

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
                                                                   
