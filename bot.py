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

# START
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    args = message.get_args()
    referral = int(args) if args else None

    database.add_user(message.from_user.id, referral)

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🛍 Mahsulotlar", callback_data="products"))
    kb.add(InlineKeyboardButton("💰 Balans", callback_data="balance"))

    if message.from_user.id == config.ADMIN_ID:
        kb.add(InlineKeyboardButton("👨‍💼 Admin", callback_data="admin"))

    await message.answer("Xush kelibsiz!", reply_markup=kb)

# PRODUCTS
@dp.callback_query_handler(lambda c: c.data == "products")
async def products(callback: types.CallbackQuery):
    products = database.get_products()

    kb = InlineKeyboardMarkup()
    for p in products:
        kb.add(InlineKeyboardButton(f"{p[1]} - {p[2]} so'm",
                                    callback_data=f"buy_{p[0]}"))

    await callback.message.edit_text("Mahsulotlar:", reply_markup=kb)

# BUY
@dp.callback_query_handler(lambda c: c.data.startswith("buy_"))
async def buy(callback: types.CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    products = database.get_products()

    for p in products:
        if p[0] == product_id:
            prices = [LabeledPrice(label=p[1], amount=p[2] * 100)]

            await bot.send_invoice(
                callback.from_user.id,
                title=p[1],
                description="To‘lov qiling",
                provider_token=config.PAYMENT_TOKEN,
                currency="UZS",
                prices=prices,
                start_parameter="shop",
                payload=str(p[0])
            )

# PRECHECK
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

# SUCCESS
@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    product_id = int(message.successful_payment.invoice_payload)
    products = database.get_products()

    for p in products:
        if p[0] == product_id:
            database.add_order(message.from_user.id, p[1], p[2])

            # referral bonus
            await message.answer("✅ To‘lov qabul qilindi!")

            await bot.send_message(
                config.ADMIN_ID,
                f"💰 Yangi to‘lov\nUser: {message.from_user.id}\n{p[1]}"
            )

# BALANCE
@dp.callback_query_handler(lambda c: c.data == "balance")
async def balance(callback: types.CallbackQuery):
    bal = database.get_balance(callback.from_user.id)
    await callback.message.answer(f"Sizning balans: {bal} so'm")

# ADMIN
@dp.callback_query_handler(lambda c: c.data == "admin")
async def admin(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📦 Buyurtmalar", callback_data="orders"))
    kb.add(InlineKeyboardButton("➕ Mahsulot qo'shish", callback_data="add_product"))
    kb.add(InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"))
    await callback.message.edit_text("Admin Panel", reply_markup=kb)

# ORDERS
@dp.callback_query_handler(lambda c: c.data == "orders")
async def orders(callback: types.CallbackQuery):
    orders = database.get_orders()
    text = ""
    for o in orders:
        text += f"{o[1]} | {o[2]} | {o[3]} so'm\n"
    await callback.message.answer(text)

# ADD PRODUCT
@dp.callback_query_handler(lambda c: c.data == "add_product")
async def add_product(callback: types.CallbackQuery):
    await callback.message.answer("Format: Nomi, Narxi")

    @dp.message_handler()
    async def save_product(message: types.Message):
        name, price = message.text.split(",")
        database.add_product(name.strip(), int(price.strip()))
        await message.answer("Mahsulot qo'shildi!")

# BROADCAST
@dp.callback_query_handler(lambda c: c.data == "broadcast")
async def broadcast(callback: types.CallbackQuery):
    await callback.message.answer("Xabar yuboring:")

    @dp.message_handler()
    async def send_all(message: types.Message):
        users = database.get_users()
        for u in users:
            try:
                await bot.send_message(u[0], message.text)
            except:
                pass
        await message.answer("Yuborildi!")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
