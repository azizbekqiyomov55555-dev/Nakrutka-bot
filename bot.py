import asyncio
import logging
import random
import string
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# --- SOZLAMALAR ---
API_TOKEN = '8066717720:AAEe3NoBcug1rTFT428HEBmJriwiutyWtr8'
ADMIN_ID = 8537782289

# Foydalanuvchi ma'lumotlarini saqlash (Oddiy misol, real loyihada DB ishlating)
user_data = {} 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- YORDAMCHI FUNKSIYALAR ---
def get_api_key(user_id):
    if user_id not in user_data:
        user_data[user_id] = {'key': ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))}
    return user_data[user_id]['key']

# --- KLAVIATURALAR ---
def main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🛍 Xizmatlar"), KeyboardButton(text="📲 Nomer olish")],
        [KeyboardButton(text="🛒 Buyurtmalarim"), KeyboardButton(text="👥 Pul ishlash")],
        [KeyboardButton(text="💰 Hisobim"), KeyboardButton(text="💰 Hisob To'ldirish")],
        [KeyboardButton(text="📩 Murojaat"), KeyboardButton(text="☎️ Qo'llab-quvvatlash")],
        [KeyboardButton(text="🤝 Hamkorlik")]
    ], resize_keyboard=True)

# --- 1-RASM: START ---
@dp.message(Command("start"))
async def start_command(message: types.Message):
    text = (
        f"👋 Assalomu alaykum! {message.from_user.first_name}\n\n"
        f"🟦 @SaleSeenBot ga xush kelibsiz!\n\n"
        f"📊 Ushbu bot orqali siz barcha platformalarga shuningdek\n"
        f"🔵 Telegram, 🟣 Instagram, ⚫️ TikTok, 🔴 YouTube va boshqa tarmoqlarga "
        f"sifatli va hamyonbop **NAKRUTKA** va Boshqa xizmatlardan foydalanishingiz mumkin 🔵\n\n"
        f"🕹 Bot qo'llanmasi: /qollanma"
    )
    await message.answer(text, reply_markup=main_menu())

# --- 2-RASM: XIZMATLAR ---
@dp.message(F.text == "🛍 Xizmatlar")
async def xizmatlar(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔵 Telegram", callback_data="tg"), InlineKeyboardButton(text="🟣 Instagram", callback_data="inst")],
        [InlineKeyboardButton(text="⚫️ TikTok", callback_data="tt"), InlineKeyboardButton(text="🔴 YouTube", callback_data="yt")],
        [InlineKeyboardButton(text="🔍 Qidirish", callback_data="search"), InlineKeyboardButton(text="🎟 2-Bo'lim", callback_data="part2")],
        [InlineKeyboardButton(text="🛒 Barcha xizmatlar", url="https://saleseen.uz")]
    ])
    await message.answer("✅ Xizmatlarimizni tanlaganingizdan xursandmiz!\n👇 Ijtimoiy tarmoqlardan birini tanlang:", reply_markup=kb)

# --- 3-4-5 RASMLAR: NOMER OLISH ---
@dp.message(F.text == "📲 Nomer olish")
async def nomer_olish(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Telegram Akauntlar", callback_data="tg_accs")],
        [InlineKeyboardButton(text="☎️ Boshqa Tarmoqlar", callback_data="other_nums")],
        [InlineKeyboardButton(text="Bosh sahifa 🔝", callback_data="home")]
    ])
    await message.answer("👇 Kerakli tarmoqni tanlang.", reply_markup=kb)

@dp.callback_query(F.data == "tg_accs")
async def tg_list(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Bangladesh 🇧🇩 - 8958 so'm", callback_data="buy_bd"), InlineKeyboardButton(text="Keniya 🇰🇪 - 11197 so'm", callback_data="buy_ken")],
        [InlineKeyboardButton(text="Hindiston 🇮🇳 - 11197 so'm", callback_data="buy_ind"), InlineKeyboardButton(text="Kolumbiya 🇨🇴 - 12317 so'm", callback_data="buy_col")],
        [InlineKeyboardButton(text="👤 Admin orqali nomer olish", url="https://t.me/SaleContact")],
        [InlineKeyboardButton(text="1/9", callback_data="page1"), InlineKeyboardButton(text="⏩ Keyingi", callback_data="next_page")]
    ])
    await callback.message.edit_text("🛍 Topilgan davlatlar ro'yxati:", reply_markup=kb)

# --- 6-RASM: PUL ISHLASH (REFERAL) ---
@dp.message(F.text == "👥 Pul ishlash")
async def pul_ishlash(message: types.Message):
    ref_link = f"https://t.me/SaleSeenBot?start=client_{message.from_user.id}"
    text = (
        f"Sizning referal havolangiz:\n\n{ref_link}\n\n"
        f"Sizga har bir taklif qilgan o'zbek referalingiz uchun 150 so'm, boshqa davlat uchun 75 so'm beriladi.\n"
        f"(Feyk reklama blockka sabab bo'ladi)\n\n"
        f"👤 ID raqam: {message.from_user.id}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💎 Haftalik referal", callback_data="weekly_ref")]])
    await message.answer(text, reply_markup=kb)

# --- 7-RASM: HISOBIM ---
@dp.message(F.text == "💰 Hisobim")
async def hisobim(message: types.Message):
    text = (
        "🏰 Kabinetingizga xush kelibsiz.\n\n"
        "📋 Ma'lumotlaringiz\n"
        f"🆔 ID raqam: {message.from_user.id}\n"
        f"💵 Hisobingiz: 0 so'm\n"
        f"✅ Kiritgan pullaringiz: 0 so'm"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Hisob To'ldirish", callback_data="pay"), InlineKeyboardButton(text="🎁 Chegirma olish", callback_data="gift")],
        [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings"), InlineKeyboardButton(text="🎫 Promo-Bonus", callback_data="promo")]
    ])
    await message.answer(text, reply_markup=kb)

# --- 9-RASM: HISOB TO'LDIRISH ---
@dp.message(F.text == "💰 Hisob To'ldirish")
async def pay_menu(message: types.Message):
    text = (
        "👇 Pastda berilgan to'lov tizimlaridan birini tanlang va to'lov summasini kiriting.\n\n"
        "⚠️ Diqqat! Barcha to'lov tizimlari 100% xavfsiz. Hisobdagi pul qaytarilmaydi!"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏦 Bank karta [ Avto ]", callback_data="p1"), InlineKeyboardButton(text="🔸 Humo | Uzcard [ Avto ]", callback_data="p2")],
        [InlineKeyboardButton(text="🅿️ PAYME [ Avto ]", callback_data="p3"), InlineKeyboardButton(text="🔵 CLICK Up [ Avto ]", callback_data="p4")],
        [InlineKeyboardButton(text="🌿 Uzcard [ Admin ]", callback_data="p5"), InlineKeyboardButton(text="📬 Chetdan to'lov [ Py ]", callback_data="p6")],
        [InlineKeyboardButton(text="💳 Barcha ilovalar [ Avto ]", callback_data="p7")],
        [InlineKeyboardButton(text="🟢 PAYNET Bankomat-Ilova", callback_data="p8")],
        [InlineKeyboardButton(text="☎️ Adminga Murojaat", url="https://t.me/SaleContact")]
    ])
    await message.answer(text, reply_markup=kb)

# --- 10-15 RASMLAR: HAMKORLIK & API ---
@dp.message(F.text == "🤝 Hamkorlik")
async def hamkorlik(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 SMM Panel API", callback_data="smm_api")],
        [InlineKeyboardButton(text="☎️ TG Nomer API", callback_data="num_api")],
        [InlineKeyboardButton(text="🤖 SMM Bot Yaratish", callback_data="make_bot")]
    ])
    await message.answer("🤝 Hamkorlik dasturi. Biz bilan yangi daromad manbaingizni yarating.\n\nTushunmasangiz: @SaleContact murojaat qiling.", reply_markup=kb)

@dp.callback_query(F.data == "num_api")
async def num_api(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 API Kalit", callback_data="get_key")],
        [InlineKeyboardButton(text="💼 Qo'llanmalar", callback_data="guide")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_ham")]
    ])
    await callback.message.edit_text("☎️ Nomer API - tizimi\n\n📋 Ushbu tizim orqali siz Tayyor Akkauntlarga API olishingiz mumkin", reply_markup=kb)

@dp.callback_query(F.data == "get_key")
async def show_key(callback: types.CallbackQuery):
    key = get_api_key(callback.from_user.id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="♻️ API kalitni yangilash", callback_data="new_key")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="num_api")]
    ])
    await callback.message.edit_text(f"Api urllar va dokumentlar 💼 Qo'llanmalar bo'limida.\n\n📋 Sizning API kalitingiz 👇:\n`{key}`", reply_markup=kb, parse_mode="Markdown")

# --- ASOSIY STARTUP ---
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    
