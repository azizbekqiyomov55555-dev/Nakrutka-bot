import asyncio
from aiohttp import web

async def handle(request):
    return web.Response(text="Bot ishlayapti")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()

async def main():
    print("Bot ishga tushdi")

    await start_web_server()

    while True:
        print("Ishlayapti...")
        await asyncio.sleep(30)
