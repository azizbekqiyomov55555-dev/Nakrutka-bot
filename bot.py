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

# --- KONFIGURATSIYA ---
API_TOKEN = '8066717720:AAEe3NoBcug1rTFT428HEBmJriwiutyWtr8'
ADMIN_ID = 8537782289 
ADMIN_USERNAME = "@Azizku_2008"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# --- FSM HOLATLARI ---
class OrderState(StatesGroup):
    waiting_for_quantity = State()
    waiting_for_link = State()

class AdminStates(StatesGroup):
    waiting_for_api_url = State()
    waiting_for_api_key = State()
    waiting_for_video = State()

# --- BAZA BILAN ISHLASH ---
def init_db():
    conn = sqlite3.connect("sale_seen.db")
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, api_key TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    conn.commit()
    conn.close()

init_db()

def get_setting(key):
    conn = sqlite3.connect("sale_seen.db")
    res = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return res[0] if res else None

# --- ASOSIY MENYULAR ---
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
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        conn.execute("INSERT INTO users (id, api_key) VALUES (?, ?)", (user_id, secrets.token_hex(16)))
        conn.commit()
    conn.close()
    await message.answer(f"👋 Assalomu alaykum! {message.from_user.first_name}\n🤖 @SaleSeenBot ga xush kelibsiz!", reply_markup=main_menu())

# --- 🛍 XIZMATLAR BO'LIMI (DINAMIK) ---
@dp.message(F.text == "🛍 Xizmatlar")
async def services_cats(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔵 Telegram", callback_data="list_Telegram"),
                types.InlineKeyboardButton(text="🟣 Instagram", callback_data="list_Instagram"))
    builder.row(types.InlineKeyboardButton(text="⚫️ TikTok", callback_data="list_TikTok"),
                types.InlineKeyboardButton(text="🔴 YouTube", callback_data="list_YouTube"))
    builder.row(types.InlineKeyboardButton(text="🔍 Qidirish", callback_data="search_ser"),
                types.InlineKeyboardButton(text="🎟 2-Bo'lim", callback_data="section_2"))
    builder.row(types.InlineKeyboardButton(text="🛒 Barcha xizmatlar", callback_data="list_all"))
    await message.answer("✅ <b>Ijtimoiy tarmoqlardan birini tanlang:</b>", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("list_"))
async def show_services(call: types.CallbackQuery):
    cat = call.data.split("_")[1]
    url = get_setting("api_url")
    key = get_setting("main_api_key")
    
    if not url or not key:
        return await call.answer("⚠️ Admin API sozlamalarini kiritmagan!", show_alert=True)

    await call.answer("Yuklanmoqda...")
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data={'key': key, 'action': 'services'}) as resp:
            data = await resp.json()
            builder = InlineKeyboardBuilder()
            for s in data:
                if cat == "all" or cat.lower() in s['name'].lower() or cat.lower() in s.get('category','').lower():
                    builder.row(types.InlineKeyboardButton(text=f"{s['name']} - {s['rate']} so'm", callback_data=f"buy_{s['service']}_{s['min']}_{s['max']}"))
            builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_cats"))
            await call.message.edit_text(f"🛍 <b>{cat} bo'yicha xizmatlar:</b>", reply_markup=builder.as_markup())

# --- 🛒 BUYURTMA BERISH JARAYONI ---
@dp.callback_query(F.data.startswith("buy_"))
async def order_step1(call: types.CallbackQuery, state: FSMContext):
    _, s_id, s_min, s_max = call.data.split("_")
    await state.update_data(s_id=s_id, min_q=s_min, max_q=s_max)
    await call.message.answer(f"🔢 <b>Miqdorni kiriting:</b>\n(Minimal: {s_min} - Maksimal: {s_max})")
    await state.set_state(OrderState.waiting_for_quantity)

@dp.message(OrderState.waiting_for_quantity)
async def order_step2(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("⚠️ Faqat raqam kiriting!")
    await state.update_data(amount=message.text)
    await message.answer("🔗 <b>Manzilni (Link/URL) kiriting:</b>")
    await state.set_state(OrderState.waiting_for_link)

@dp.message(OrderState.waiting_for_link)
async def order_final(message: types.Message, state: FSMContext):
    data = await state.get_data()
    # Bu yerda API orqali panelga buyurtma yuborish logikasi bo'ladi
    await message.answer(f"✅ <b>Buyurtma qabul qilindi!</b>\n\nXizmat ID: {data['s_id']}\nMiqdor: {data['amount']}\nManzil: {message.text}")
    await state.clear()

# --- 🤝 HAMKORLIK BO'LIMI ---
@dp.message(F.text == "🤝 Hamkorlik")
async def hamkorlik(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔥 SMM Panel API", callback_data="h_smm"),
                types.InlineKeyboardButton(text="☎️ TG Nomer API", callback_data="h_nomer"))
    builder.row(types.InlineKeyboardButton(text="🤖 SMM Bot Yaratish", callback_data="h_bot"))
    builder.adjust(1)
    await message.answer("🤝 <b>Hamkorlik dasturi. Kerakli bo'limni tanlang:</b>", reply_markup=builder.as_markup())

@dp.callback_query(F.data.in_(["h_smm", "h_nomer"]))
async def hamkorlik_api(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔑 API Kalit", callback_data="view_keys"),
                types.InlineKeyboardButton(text="💼 Qo'llanmalar", callback_data="view_guide"))
    builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_collab"))
    title = "SMM Panel" if call.data == "h_smm" else "Nomer API"
    await call.message.edit_text(f"🔥 <b>{title} - tizimi</b>\n\n📋 Ushbu tizim orqali siz API ulab ishlashingiz mumkin.", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "view_keys")
async def view_keys(call: types.CallbackQuery):
    conn = sqlite3.connect("sale_seen.db")
    u = conn.execute("SELECT api_key FROM users WHERE id = ?", (call.from_user.id,)).fetchone()
    conn.close()
    txt = f"📌 <b>URL:</b> <code>https://saleseen.uz/api/v2</code>\n📋 <b>API Key:</b> <code>{u[0]}</code>"
    builder = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="♻️ Yangilash", callback_data="ref_key"), types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_collab"))
    await call.message.edit_text(txt, reply_markup=builder.as_markup())

# --- 📲 NOMER OLISH (TO'LIQ RO'YXAT) ---
@dp.message(F.text == "📲 Nomer olish")
async def nomer_menu(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="📞 Telegram Akauntlar"), types.KeyboardButton(text="☎️ Boshqa Tarmoqlar"))
    builder.row(types.KeyboardButton(text="Bosh sahifa ⬆️"))
    await message.answer("👇 Kerakli tarmoqni tanlang.", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(F.text == "📞 Telegram Akauntlar")
@dp.callback_query(F.data == "tg_1")
async def tg_page1(event):
    builder = InlineKeyboardBuilder()
    countries = [("Bangladesh 🇧🇩 - 8958", "b"), ("Hindiston 🇮🇳 - 11197", "b"), ("Keniya 🇰🇪 - 11197", "b"), ("Kolumbiya 🇨🇴 - 12317", "b"), ("Azerbaijan 🇦🇿 - 13437", "b"), ("Dominikana 🇩🇴 - 13437", "b"), ("Shri Lanka 🇱🇰 - 14556", "b"), ("Marokash 🇲🇦 - 14556", "b"), ("Tanzaniya 🇹🇿 - 14556", "b"), ("Zambiya 🇿🇲 - 14556", "b")]
    for t, c in countries: builder.add(types.InlineKeyboardButton(text=t, callback_data=c))
    builder.adjust(2)
    builder.row(types.InlineKeyboardButton(text="🥷 Admin orqali olish", url=f"https://t.me/{ADMIN_USERNAME.replace('@','') }"))
    builder.row(types.InlineKeyboardButton(text="1/9", callback_data="none"), types.InlineKeyboardButton(text="⏩ Keyingi", callback_data="tg_2"))
    
    txt = "📞 <b>Telegram akaunt ochish uchun raqamlar:</b>"
    if isinstance(event, types.Message): await event.answer(txt, reply_markup=builder.as_markup())
    else: await event.message.edit_text(txt, reply_markup=builder.as_markup())

# --- ADMIN PANEL ---
@dp.message(Command("admin"), F.from_user.id == ADMIN_ID)
async def admin_main(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⚙️ SMM URL", callback_data="set_url"), types.InlineKeyboardButton(text="🔑 SMM KEY", callback_data="set_key"))
    builder.row(types.InlineKeyboardButton(text="🎥 Video Yuklash", callback_data="set_vid"))
    await message.answer("🛠 <b>Admin Panel</b>", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "set_url")
async def set_url(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("🔗 API URL yuboring:"); await state.set_state(AdminStates.waiting_for_api_url)

@dp.message(AdminStates.waiting_for_api_url)
async def save_url(message: types.Message, state: FSMContext):
    conn = sqlite3.connect("sale_seen.db")
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('api_url', ?)", (message.text,))
    conn.commit(); conn.close()
    await message.answer("✅ URL saqlandi!"); await state.clear()

@dp.message(F.text == "Bosh sahifa ⬆️")
async def go_home(message: types.Message):
    await message.answer("Asosiy menyu", reply_markup=main_menu())

@dp.callback_query(F.data == "back_to_cats")
async def back_cats(call: types.CallbackQuery): await services_cats(call.message)

@dp.callback_query(F.data == "back_collab")
async def back_h(call: types.CallbackQuery): await hamkorlik(call.message)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
            
