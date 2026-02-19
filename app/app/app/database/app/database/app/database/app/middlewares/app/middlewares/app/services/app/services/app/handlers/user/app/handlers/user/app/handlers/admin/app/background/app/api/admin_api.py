from fastapi import FastAPI
from app.database.engine import SessionLocal
from app.database.models import User
from sqlalchemy import select

app = FastAPI()

@app.get("/users")
async def get_users():
    async with SessionLocal() as session:
        result = await session.execute(select(User))
        return result.scalars().all()
