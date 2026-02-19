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

# --- FSM (Admin Panel uchun) ---
class AdminStates(StatesGroup):
    waiting_for_api_url = State()
    waiting_for_api_key = State()
    waiting_for_video = State()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# --- BAZA BILAN ISHLASH ---
def get_db_connection():
    conn = sqlite3.connect("sale_seen.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, api_key TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
init_db()

# --- REPLAY MENYULAR (ASOSIY) ---
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
    with get_db_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            conn.execute("INSERT INTO users (id, api_key) VALUES (?, ?)", (user_id, secrets.token_hex(16)))
    
    await message.answer(f"👋 Assalomu alaykum! {message.from_user.first_name}\n\n🤖 @SaleSeenBot ga xush kelibsiz!", reply_markup=main_menu())

# --- XIZMATLAR BO'LIMI (Skrinshotdagi dizayn) ---
@dp.message(F.text == "🛍 Xizmatlar")
async def services_category(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔵 Telegram", callback_data="cat_telegram"),
                types.InlineKeyboardButton(text="🟣 Instagram", callback_data="cat_instagram"))
    builder.row(types.InlineKeyboardButton(text="⚫️ TikTok", callback_data="cat_tiktok"),
                types.InlineKeyboardButton(text="🔴 YouTube", callback_data="cat_youtube"))
    builder.row(types.InlineKeyboardButton(text="🔍 Qidirish", callback_data="search_ser"),
                types.InlineKeyboardButton(text="🎟 2-Bo'lim", callback_data="section_2"))
    builder.row(types.InlineKeyboardButton(text="🛒 Barcha xizmatlar", callback_data="all_services"))
    builder.row(types.InlineKeyboardButton(text="⏪ Orqaga", callback_data="back_home"))
    
    text = "✅ <b>Xizmatlarimizni tanlaganingizdan xursandmiz!</b>\n\n👇 <b>Ijtimoiy tarmoqlardan birini tanlang:</b>"
    await message.answer(text, reply_markup=builder.as_markup())

# --- HAMKORLIK BO'LIMI ---
@dp.message(F.text == "🤝 Hamkorlik")
async def collab_menu(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔥 SMM Panel API", callback_data="sect_smm"))
    builder.row(types.InlineKeyboardButton(text="☎️ TG Nomer API", callback_data="sect_nomer"))
    builder.row(types.InlineKeyboardButton(text="🤖 SMM Bot Yaratish", callback_data="sect_bot"))
    builder.adjust(1)
    
    text = (
        "🤝 <b>Hamkorlik dastro'ri. Biz bilan yangi daromad manbaingizni yarating.</b>\n\n"
        "<i>Tushunmasangiz: @SaleContact murojat qilishingiz mumkin.</i>\n\n"
        "📋 <b>Kerakli bo'limni tanlang:</b>"
    )
    await message.answer(text, reply_markup=builder.as_markup())

# --- SMM PANEL API BO'LIMI ---
@dp.callback_query(F.data == "sect_smm")
async def sect_smm_handler(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔑 API Kalit", callback_data="view_my_api"),
                types.InlineKeyboardButton(text="💼 Qo'llanmalar", callback_data="guide_video_view"))
    builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_collab"))
    
    text = "🔥 <b>SMM Panel - tizimi</b>\n\n📋 Ushbu tizim orqali siz SMM xizmatlariga API orqali buyurtma qilishingiz mumkin"
    await call.message.edit_text(text, reply_markup=builder.as_markup())

@dp.callback_query(F.data == "view_my_api")
async def view_api_handler(call: types.CallbackQuery):
    user_id = call.from_user.id
    with get_db_connection() as conn:
        user = conn.execute("SELECT api_key FROM users WHERE id = ?", (user_id,)).fetchone()
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="♻️ API kalitni yangilash", callback_data="refresh_key"))
    builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="sect_smm"))
    
    text = (
        f"📌 <b>Sizning API Manzilingiz</b> 👇:\n<code>https://saleseen.uz/api/v2</code>\n\n"
        f"📋 <b>Sizning API kalitingiz</b> 👇:\n<code>{user['api_key']}</code>"
    )
    await call.message.edit_text(text, reply_markup=builder.as_markup())

# --- NOMER OLISH (TELEGRAM AKAUNTLAR) ---
@dp.message(F.text == "📲 Nomer olish")
async def nomer_olish_start(message: types.Message):
    await message.answer("👇 Kerakli tarmoqni tanlang.", reply_markup=nomer_menu())

@dp.message(F.text == "📞 Telegram Akauntlar")
@dp.callback_query(F.data == "tg_page_1")
async def tg_akauntlar_p1(event):
    builder = InlineKeyboardBuilder()
    p1_data = [
        ("Bangladesh 🇧🇩 - 8958", "buy"), ("Hindiston 🇮🇳 - 11197", "buy"),
        ("Keniya 🇰🇪 - 11197", "buy"), ("Kolumbiya 🇨🇴 - 12317", "buy"),
        ("Azerbaijan 🇦🇿 - 13437", "buy"), ("Dominikana 🇩🇴 - 13437", "buy"),
        ("Shri Lanka 🇱🇰 - 14556", "buy"), ("Marokash 🇲🇦 - 14556", "buy"),
        ("Tanzaniya 🇹🇿 - 14556", "buy"), ("Zambiya 🇿🇲 - 14556", "buy"),
        ("Kongo 🇨🇬 - 14556", "buy"), ("Kosta-Rika 🇨🇷 - 14556", "buy"),
        ("Misr 🇪🇬 - 14556", "buy"), ("Madagaskar 🇲🇬 - 15676", "buy"),
        ("Rwanda 🇷🇼 - 15676", "buy"), ("Jazoir 🇩🇿 - 15676", "buy")
    ]
    for text, cb in p1_data: builder.add(types.InlineKeyboardButton(text=text, callback_data=cb))
    builder.adjust(2)
    builder.row(types.InlineKeyboardButton(text="🥷 Admin orqali nomer olish", url=f"https://t.me/{ADMIN_USERNAME.replace('@','') }"))
    builder.row(types.InlineKeyboardButton(text="1/9", callback_data="none"), types.InlineKeyboardButton(text="⏩ Keyingi", callback_data="tg_page_2"))
    
    text = "📞 <b>Ushbu davlat raqamlari faqat Telegram akaunt ochish uchun beriladi.</b>\n\n🛍 <b>Topilgan davlatlar ro'yxati:</b>"
    if isinstance(event, types.Message): await event.answer(text, reply_markup=builder.as_markup())
    else: await event.message.edit_text(text, reply_markup=builder.as_markup())

@dp.callback_query(F.data == "tg_page_2")
async def tg_akauntlar_p2(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    p2_data = [
        ("Puerto-Riko 🇵🇷 - 15676", "buy"), ("Argentina 🇦🇷 - 15676", "buy"),
        ("AQSh 🇺🇸 - 16796", "buy"), ("Afg'oniston 🇦🇫 - 16796", "buy"),
        ("Gaiti 🇭🇹 - 16796", "buy"), ("Yamayka 🇯🇲 - 16796", "buy"),
        ("Barbuda 🇦🇬 - 17916", "buy"), ("Trinidad 🇹🇹 - 17916", "buy"),
        ("Nikaragua 🇳🇮 - 17916", "buy"), ("Mavritaniya 🇲🇷 - 17916", "buy"),
        ("Venesuela 🇻🇪 - 17916", "buy"), ("O'zbekiston 🇺🇿 - 17916", "buy")
    ]
    for text, cb in p2_data: builder.add(types.InlineKeyboardButton(text=text, callback_data=cb))
    builder.adjust(2)
    builder.row(types.InlineKeyboardButton(text="🥷 Admin orqali nomer olish", url=f"https://t.me/{ADMIN_USERNAME.replace('@','') }"))
    builder.row(types.InlineKeyboardButton(text="⏪ Oldingi", callback_data="tg_page_1"), types.InlineKeyboardButton(text="2/9", callback_data="none"), types.InlineKeyboardButton(text="⏩ Keyingi", callback_data="tg_page_3"))
    await call.message.edit_text("📞 <b>Ushbu davlat raqamlari faqat Telegram akaunt ochish uchun beriladi.</b>\n\n🛍 <b>Topilgan davlatlar ro'yxati:</b>", reply_markup=builder.as_markup())

# --- ADMIN PANEL ---
@dp.message(Command("admin"), F.from_user.id == ADMIN_ID)
async def admin_panel(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⚙️ API Sozlash", callback_data="adm_api"))
    builder.row(types.InlineKeyboardButton(text="🎥 Video Yuklash", callback_data="adm_video"))
    await message.answer("🛠 <b>Admin Panel</b>", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "adm_video", F.from_user.id == ADMIN_ID)
async def adm_video_prompt(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("🎥 Hamkorlik qo'llanmasi uchun videoni yuboring:")
    await state.set_state(AdminStates.waiting_for_video)

@dp.message(AdminStates.waiting_for_video, F.video)
async def adm_video_save(message: types.Message, state: FSMContext):
    with get_db_connection() as conn:
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('guide_video', ?)", (message.video.file_id,))
    await message.answer("✅ Video saqlandi!")
    await state.clear()

@dp.callback_query(F.data == "guide_video_view")
async def view_guide(call: types.CallbackQuery):
    with get_db_connection() as conn:
        video = conn.execute("SELECT value FROM settings WHERE key = 'guide_video'").fetchone()
    if video:
        await call.message.answer_video(video=video['value'], caption="🎥 Hamkorlik bo'yicha qo'llanma")
    else:
        await call.answer("⚠️ Video yuklanmagan!", show_alert=True)

# --- QAYTISH ---
@dp.message(F.text == "Bosh sahifa ⬆️")
async def back_to_home(message: types.Message):
    await message.answer("Asosiy menyuga qaytdingiz.", reply_markup=main_menu())

@dp.callback_query(F.data == "back_to_collab")
async def back_collab(call: types.CallbackQuery):
    await collab_menu(call.message)

# --- ISHGA TUSHIRISH ---
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    
