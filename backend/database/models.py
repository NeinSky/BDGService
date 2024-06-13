from sqlalchemy import Column, Integer, VARCHAR, Date, Sequence, BOOLEAN, update, delete, select, func
from sqlalchemy.orm import declarative_base

from .connection import get_session
from config import logger, AUTH_CREATE_DEFAULT_ADMIN, AUTH_DEFAULT_ADMIN, AUTH_DEFAULT_ADMIN_PASSWORD
from auth.shared import pwd_context
from auth.models import User, UserInDB

Base = declarative_base()

# "johndoe": {
#     "username": "johndoe",
#     "full_name": "John Doe",
#     "email": "johndoe@example.com",
#     "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
#     "disabled": False,
# }


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, Sequence('admins_id_seq'), primary_key=True)
    username = Column(VARCHAR(50), nullable=False, unique=True)
    password = Column(VARCHAR(60), nullable=False)
    full_name = Column(VARCHAR(50), default='')
    email = Column(VARCHAR(100), default='')
    disabled = Column(BOOLEAN, default=False)

    @staticmethod
    async def create_default_admin() -> None:
        """
        Создаёт администратора по умолчанию, если таблица администраторов пуста и включена соответствующая настройка.

        :return:
        """
        if AUTH_CREATE_DEFAULT_ADMIN:
            async with get_session() as session:
                r = await session.execute(select(Admin).limit(1))
                admin = r.scalars().all()
                if not admin and AUTH_CREATE_DEFAULT_ADMIN:
                    logger.info(f'Таблица администраторов пуста. Создана запись по умолчанию: {AUTH_DEFAULT_ADMIN}')
                    session.add(Admin(
                        username=AUTH_DEFAULT_ADMIN,
                        password=pwd_context.hash(AUTH_DEFAULT_ADMIN_PASSWORD),
                    ))
                    await session.commit()

    @staticmethod
    async def get_admin(username: str):
        async with get_session() as session:
            r = await session.execute(
                select(Admin).where(Admin.username == username)
            )
            return r.scalar_one_or_none()

