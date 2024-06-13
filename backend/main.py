from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes import hello, auth
from database.models import Base, Admin
from database.connection import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await Admin.create_default_admin()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(hello.router)
app.include_router(auth.router)
