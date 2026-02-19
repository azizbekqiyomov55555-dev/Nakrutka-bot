from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from aiogram.utils import executor
import logging
import config
import database

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

database.create_tables()

PRODUCT = {
    "name": "Premium Xizmat",
    "price": 10000
}

# /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    database.add_user(message.from_user.id)

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🛍 Sotib olish", callback_data="buy"))

    if message.from_user.id == config.ADMIN_ID:
        kb.add(InlineKeyboardButton("👨‍💼 Admin Panel", callback_data="admin"))

    await message.answer("Xizmatni tanlang:", reply_markup=kb)

# Buy tugmasi
@dp.callback_query_handler(lambda c: c.data == "buy")
async def buy(callback: types.CallbackQuery):
    prices = [LabeledPrice(label=PRODUCT["name"], amount=PRODUCT["price"] * 100)]

    await bot.send_invoice(
        callback.from_user.id,
        title=PRODUCT["name"],
        description="To‘lovni amalga oshiring",
        provider_token=config.PAYMENT_TOKEN,
        currency="UZS",
        prices=prices,
        start_parameter="create_invoice",
        payload="shop_payment"
    )

# To‘lovdan oldingi tekshiruv
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

# To‘lov muvaffaqiyatli
@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    database.add_order(
        message.from_user.id,
        PRODUCT["name"],
        PRODUCT["price"]
    )

    await message.answer("✅ To‘lov qabul qilindi!")

    await bot.send_message(
        config.ADMIN_ID,
        f"💰 Yangi to‘lov!\nUser: {message.from_user.id}\nSumma: {PRODUCT['price']}"
    )

# Admin panel
@dp.callback_query_handler(lambda c: c.data == "admin")
async def admin_panel(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📦 Buyurtmalar", callback_data="orders"))
    kb.add(InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"))
    await callback.message.edit_text("Admin Panel", reply_markup=kb)

# Buyurtmalarni ko‘rish
@dp.callback_query_handler(lambda c: c.data == "orders")
async def show_orders(callback: types.CallbackQuery):
    orders = database.get_orders()
    text = "📦 Buyurtmalar:\n\n"
    for o in orders:
        text += f"ID:{o[0]} | User:{o[1]} | {o[2]} | {o[3]} so'm\n"

    await callback.message.answer(text)

# Broadcast
@dp.callback_query_handler(lambda c: c.data == "broadcast")
async def broadcast(callback: types.CallbackQuery):
    await callback.message.answer("Xabar matnini yuboring:")

    @dp.message_handler()
    async def send_all(message: types.Message):
        users = database.get_users()
        for u in users:
            try:
                await bot.send_message(u[0], message.text)
            except:
                pass

        await message.answer("✅ Xabar yuborildi!")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
