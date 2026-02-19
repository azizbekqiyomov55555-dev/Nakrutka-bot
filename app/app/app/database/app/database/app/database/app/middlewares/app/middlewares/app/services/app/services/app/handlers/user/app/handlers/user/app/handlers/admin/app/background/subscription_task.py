import asyncio
from datetime import datetime
from app.database.engine import SessionLocal
from app.database.models import Subscription

async def check_subscriptions():
    while True:
        async with SessionLocal() as session:
            subs = await session.execute(Subscription.__table__.select())
            for sub in subs:
                if sub.expires_at < datetime.utcnow():
                    await session.delete(sub)
            await session.commit()
        await asyncio.sleep(3600)
