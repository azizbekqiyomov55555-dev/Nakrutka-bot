from app.database.engine import SessionLocal
from app.database.models import User, Transaction

async def deposit(user_id: int, amount: int):
    async with SessionLocal() as session:
        user = await session.get(User, user_id)
        user.balance += amount
        session.add(Transaction(user_id=user_id, amount=amount, type="deposit"))
        await session.commit()
