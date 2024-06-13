from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.pool import NullPool

from contextlib import asynccontextmanager
from config import DB_DRIVER, DB_USER, DB_PASSWORD, DB_PORT, DB_NAME, DB_HOST, DB_ECHO, logger

engine = create_async_engine(
    f'{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
    echo=DB_ECHO,
    poolclass=NullPool,
)


def async_session_generator():
    return sessionmaker(
        engine, class_=AsyncSession
    )


@asynccontextmanager
async def get_session():
    try:
        async_session = async_session_generator()

        async with async_session() as session:
            yield session
    except Exception as ex:
        logger.warning(f'{str(ex)}   rolling back.')
        await session.rollback()
        raise
    finally:
        await session.close()
