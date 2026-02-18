import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

TOKEN = "BOT_TOKEN"
API_URL = "https://panelapi.example.com/api/v2"
API_KEY = "API_KEY"

bot = Bot(TOKEN)
dp = Dispatcher()

# ===== MENU =====

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 Xizmatlar")],
        [KeyboardButton(text="💰 Balans")],
        [KeyboardButton(text="📦 Buyurtma berish")]
    ],
    resize_keyboard=True
)

# ===== API FUNCTIONS =====

async def api_request(data):
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, data=data) as r:
            return await r.json()

async def get_services():
    return await api_request({
        "key": API_KEY,
        "action": "services"
    })

async def get_balance():
    return await api_request({
        "key": API_KEY,
        "action": "balance"
    })

async def create_order(service, link, quantity):
    return await api_request({
        "key": API_KEY,
        "action": "add",
        "service": service,
        "link": link,
        "quantity": quantity
    })

# ===== START =====

@dp.message(CommandStart())
async def start(msg: Message):
    await msg.answer("👋 Nakrutka botga xush kelibsiz!", reply_markup=menu)

# ===== BALANCE =====

@dp.message(F.text == "💰 Balans")
async def balance(msg: Message):
    data = await get_balance()

    if "balance" in data:
        await msg.answer(f"💰 Balans: {data['balance']}")
    else:
        await msg.answer("❌ Balans olinmadi")

# ===== SERVICES =====

@dp.message(F.text == "🛍 Xizmatlar")
async def services(msg: Message):
    await msg.answer("⏳ Yuklanmoqda...")

    data = await get_services()

    if isinstance(data, list):
        text = "📦 Xizmatlar:\n\n"

        for s in data[:15]:
            text += f"🆔 {s['service']}\n{s['name']}\n💰 {s['rate']}\n\n"

        await msg.answer(text)
    else:
        await msg.answer("❌ API xato")

# ===== ORDER FLOW =====

user_state = {}

@dp.message(F.text == "📦 Buyurtma berish")
async def order_start(msg: Message):
    user_state[msg.from_user.id] = {}
    await msg.answer("🆔 Xizmat ID kiriting:")

@dp.message()
async def order_process(msg: Message):
    uid = msg.from_user.id

    if uid not in user_state:
        return

    state = user_state[uid]

    if "service" not in state:
        state["service"] = msg.text
        await msg.answer("🔗 Link yuboring:")
        return

    if "link" not in state:
        state["link"] = msg.text
        await msg.answer("🔢 Miqdor kiriting:")
        return

    if "quantity" not in state:
        state["quantity"] = msg.text

        await msg.answer("⏳ Buyurtma yuborilmoqda...")

        result = await create_order(
            state["service"],
            state["link"],
            state["quantity"]
        )

        if "order" in result:
            await msg.answer(f"✅ Buyurtma yaratildi!\nID: {result['order']}")
        else:
            await msg.answer("❌ Buyurtma xato")

        del user_state[uid]

# ===== RUN =====

async def main():
    print("✅ Nakrutka bot ishga tushdi")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
