import asyncio
from app.bot import dp, bot
from app.db import init_db

async def main():
    await init_db()
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
