import asyncio
import uvloop
from app.loader import dp, bot
from app.database.init_db import init_db
from app.handlers.user import start, games
from app.handlers.admin import panel
from app.middlewares.auth import AuthMiddleware
from app.middlewares.ratelimit import RateLimitMiddleware
from app.background.subscription_task import check_subscriptions

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

def register():
    dp.include_router(start.router)
    dp.include_router(games.router)
    dp.include_router(panel.router)

async def main():
    await init_db()

    dp.message.middleware(AuthMiddleware())
    dp.message.middleware(RateLimitMiddleware())

    register()

    asyncio.create_task(check_subscriptions())

    await dp.start_polling(bot)
