from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes import auth, users
from database.models import Base, User
from database.connection import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await User.create_default_admin()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(users.router)
