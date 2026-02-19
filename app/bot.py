import asyncio
import os
from aiohttp import web

async def handle(request):
    return web.Response(text="Bot ishlayapti")

async def main():
    print("Bot ishga tushdi")

    app = web.Application()
    app.router.add_get("/", handle)

    port = int(os.environ.get("PORT", 8000))

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    while True:
        await asyncio.sleep(3600)
