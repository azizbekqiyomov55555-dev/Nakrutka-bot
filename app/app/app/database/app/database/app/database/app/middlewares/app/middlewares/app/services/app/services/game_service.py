import random
from app.database.engine import SessionLocal
from app.database.models import Transaction, User

async def slot(user: User, bet: int):
    if user.balance < bet:
        return "Balans yetarli emas"

    symbols = ["🍒", "🍋", "💎", "7️⃣"]
    result = [random.choice(symbols) for _ in range(3)]

    async with SessionLocal() as session:
        if result.count(result[0]) == 3:
            reward = bet * 5
            user.balance += reward
            session.add(Transaction(user_id=user.id, amount=reward, type="win"))
        else:
            user.balance -= bet

        await session.commit()

    return " ".join(result)
