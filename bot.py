import logging
import sqlite3
import asyncio
import secrets
import aiohttp # API bilan ishlash uchun kerak: pip install aiohttp
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

# --- FSM STATES (Admin panel uchun) ---
class AdminStates(StatesGroup):
    waiting_for_api_url = State()
    waiting_for_api_key = State()
    waiting_for_video = State()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# --- BAZA ---
def get_db_connection():
    conn = sqlite3.connect("sale_seen.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, 
            balance INTEGER DEFAULT 0,
            api_key TEXT)""")
        # Admin sozlamalari uchun yangi jadval
        conn.execute("""CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY, 
            value TEXT)""")
init_db()

# --- ADMIN PANEL (Faqat ADMIN_ID uchun) ---
@dp.message(Command("admin"), F.from_user.id == ADMIN_ID)
async def admin_main(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⚙️ API Sozlash", callback_data="adm_api"))
    builder.row(types.InlineKeyboardButton(text="🎥 Qo'llanma Videosini yuklash", callback_data="adm_video"))
    await message.answer("🛠 <b>Admin Paneliga xush kelibsiz!</b>", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "adm_api", F.from_user.id == ADMIN_ID)
async def adm_api_url(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("🔗 Xizmatlar uchun <b>API URL</b> manzilingizni yuboring:")
    await state.set_state(AdminStates.waiting_for_api_url)

@dp.message(AdminStates.waiting_for_api_url)
async def adm_save_url(message: types.Message, state: FSMContext):
    with get_db_connection() as conn:
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('api_url', ?)", (message.text,))
    await message.answer("✅ URL saqlandi. Endi <b>API KEY</b> (kalit)ni yuboring:")
    await state.set_state(AdminStates.waiting_for_api_key)

@dp.message(AdminStates.waiting_for_api_key)
async def adm_save_key(message: types.Message, state: FSMContext):
    with get_db_connection() as conn:
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('main_api_key', ?)", (message.text,))
    await message.answer("🎉 API sozlamalari saqlandi! Bot endi xizmatlarni avtomatik oladi.")
    await state.clear()

@dp.callback_query(F.data == "adm_video", F.from_user.id == ADMIN_ID)
async def adm_video_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("🎥 Qo'llanma sifatida ishlatiladigan videoni yuboring:")
    await state.set_state(AdminStates.waiting_for_video)

@dp.message(AdminStates.waiting_for_video, F.video)
async def adm_save_video(message: types.Message, state: FSMContext):
    file_id = message.video.file_id
    with get_db_connection() as conn:
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('guide_video', ?)", (file_id,))
    await message.answer("✅ Qo'llanma videosi muvaffaqiyatli saqlandi!")
    await state.clear()

# --- XIZMATLARNI API DAN OLISH ---
@dp.message(F.text == "🛍 Xizmatlar")
async def show_services(message: types.Message):
    with get_db_connection() as conn:
        url = conn.execute("SELECT value FROM settings WHERE key = 'api_url'").fetchone()
        key = conn.execute("SELECT value FROM settings WHERE key = 'main_api_key'").fetchone()
    
    if not url or not key:
        return await message.answer("❌ Xizmatlar vaqtincha mavjud emas (Admin API sozlamagan).")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url['value'], data={'key': key['value'], 'action': 'services'}) as resp:
                services = await resp.json()
                builder = InlineKeyboardBuilder()
                # Dastlabki 15 ta xizmatni chiqarish
                for s in services[:15]:
                    builder.row(types.InlineKeyboardButton(text=f"{s['name']} - {s['rate']} so'm", callback_data=f"buy_{s['service']}"))
                await message.answer("🛍 <b>Mavjud xizmatlar:</b>", reply_markup=builder.as_markup())
        except:
            await message.answer("⚠️ API orqali xizmatlarni yuklashda xatolik yuz berdi.")

# --- HAMKORLIK VA QO'LLANMA ---
@dp.message(F.text == "🤝 Hamkorlik")
async def collab_menu(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔥 SMM Panel API", callback_data="sect_smm"))
    builder.row(types.InlineKeyboardButton(text="☎️ TG Nomer API", callback_data="sect_nomer"))
    builder.row(types.InlineKeyboardButton(text="💼 Qo'llanma (Video)", callback_data="guide_video_view"))
    builder.adjust(1)
    await message.answer("🤝 <b>Hamkorlik dasturi...</b>", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "guide_video_view")
async def view_guide(call: types.CallbackQuery):
    with get_db_connection() as conn:
        video = conn.execute("SELECT value FROM settings WHERE key = 'guide_video'").fetchone()
    
    if video:
        await call.message.answer_video(video=video['value'], caption="📖 Hamkorlik bo'yicha video qo'llanma")
    else:
        await call.answer("⚠️ Qo'llanma videosi hali yuklanmagan.", show_alert=True)

# --- REPLAY MENYULAR (Sizning kodingiz o'zgarmadi) ---
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

# --- START VA NOMERLAR (Sizning kodingiz o'zgarmadi) ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    with get_db_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            conn.execute("INSERT INTO users (id, api_key) VALUES (?, ?)", (user_id, secrets.token_hex(16)))
    await message.answer(f"👋 Assalomu alaykum! {message.from_user.first_name}\n\n🤖 @SaleSeenBot ga xush kelibsiz!", reply_markup=main_menu())

@dp.message(F.text == "📲 Nomer olish")
async def nomer_olish_start(message: types.Message):
    await message.answer("👇 Kerakli tarmoqni tanlang.", reply_markup=nomer_menu())

@dp.message(F.text == "📞 Telegram Akauntlar")
@dp.callback_query(F.data == "tg_page_1")
async def tg_akauntlar_p1(event):
    builder = InlineKeyboardBuilder()
    p1_data = [("Bangladesh 🇧🇩 - 8958", "buy"), ("Hindiston 🇮🇳 - 11197", "buy"), ("Keniya 🇰🇪 - 11197", "buy"), ("Kolumbiya 🇨🇴 - 12317", "buy"), ("Azerbaijan 🇦🇿 - 13437", "buy"), ("Dominikana 🇩🇴 - 13437", "buy"), ("Shri Lanka 🇱🇰 - 14556", "buy"), ("Marokash 🇲🇦 - 14556", "buy"), ("Tanzaniya 🇹🇿 - 14556", "buy"), ("Zambiya 🇿🇲 - 14556", "buy"), ("Kongo 🇨🇬 - 14556", "buy"), ("Kosta-Rika 🇨🇷 - 14556", "buy"), ("Misr 🇪🇬 - 14556", "buy"), ("Madagaskar 🇲🇬 - 15676", "buy"), ("Rwanda 🇷🇼 - 15676", "buy"), ("Jazoir 🇩🇿 - 15676", "buy")]
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
    p2_data = [("Puerto-Riko 🇵🇷 - 15676", "buy"), ("Argentina 🇦🇷 - 15676", "buy"), ("AQSh 🇺🇸 - 16796", "buy"), ("Afg'oniston 🇦🇫 - 16796", "buy"), ("Gaiti 🇭🇹 - 16796", "buy"), ("Yamayka 🇯🇲 - 16796", "buy"), ("Barbuda 🇦🇬 - 17916", "buy"), ("Trinidad 🇹🇹 - 17916", "buy"), ("Nikaragua 🇳🇮 - 17916", "buy"), ("Mavritaniya 🇲🇷 - 17916", "buy"), ("Venesuela 🇻🇪 - 17916", "buy"), ("O'zbekiston 🇺🇿 - 17916", "buy"), ("Surinam 🇸🇷 - 19035", "buy"), ("Serbiya 🇷🇸 - 19035", "buy"), ("Braziliya 🇧🇷 - 19035", "buy"), ("Kuba 🇨🇺 - 19035", "buy")]
    for text, cb in p2_data: builder.add(types.InlineKeyboardButton(text=text, callback_data=cb))
    builder.adjust(2)
    builder.row(types.InlineKeyboardButton(text="🥷 Admin orqali nomer olish", url=f"https://t.me/{ADMIN_USERNAME.replace('@','') }"))
    builder.row(types.InlineKeyboardButton(text="⏪ Oldingi", callback_data="tg_page_1"), types.InlineKeyboardButton(text="2/9", callback_data="none"), types.InlineKeyboardButton(text="⏩ Keyingi", callback_data="tg_page_3"))
    await call.message.edit_text("📞 <b>Ushbu davlat raqamlari faqat Telegram akaunt ochish uchun beriladi.</b>\n\n🛍 <b>Topilgan davlatlar ro'yxati:</b>", reply_markup=builder.as_markup())

@dp.message(F.text == "Bosh sahifa ⬆️")
async def back_to_home(message: types.Message):
    await message.answer("Asosiy menyuga qaytdingiz.", reply_markup=main_menu())

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    
