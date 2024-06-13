from sqlalchemy import (Column, Integer, VARCHAR, Date, Sequence,
                        BOOLEAN, update, delete, select, ForeignKey, Table)
from sqlalchemy.orm import declarative_base
from typing import List, Dict, Any
from datetime import datetime

from .connection import get_session
from config import logger, AUTH_CREATE_DEFAULT_ADMIN, AUTH_DEFAULT_ADMIN, AUTH_DEFAULT_ADMIN_PASSWORD
from auth.shared import pwd_context
from routes.models import UserOut, UserWithPassword, UserShort

Base = declarative_base()

subscription = Table(
    "subscriptions",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("sub_id", ForeignKey("users.id"), primary_key=True),
)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('admins_id_seq'), primary_key=True)
    username = Column(VARCHAR(50), nullable=False, unique=True)
    password = Column(VARCHAR(60), nullable=False)
    full_name = Column(VARCHAR(50), default='')
    email = Column(VARCHAR(100), default='')
    birthday = Column(Date, nullable=False)
    is_admin = Column(BOOLEAN, default=False)
    disabled = Column(BOOLEAN, default=False)

    def to_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in
                self.__table__.columns}

    @staticmethod
    async def create_default_admin() -> None:
        """
        Создаёт администратора по умолчанию, если в таблице нет ни одного администратора и настройка включена
        """
        if AUTH_CREATE_DEFAULT_ADMIN:
            async with get_session() as session:
                r = await session.execute(select(User).where(User.is_admin == True).limit(1))
                admin = r.scalars().all()
                if not admin and AUTH_CREATE_DEFAULT_ADMIN:
                    logger.info(f'Таблица администраторов пуста. Создана запись по умолчанию: {AUTH_DEFAULT_ADMIN}')
                    session.add(User(
                        username=AUTH_DEFAULT_ADMIN,
                        password=pwd_context.hash(AUTH_DEFAULT_ADMIN_PASSWORD),
                        full_name='Администратор по умолчанию',
                        birthday=datetime(1900, 1, 1),
                        is_admin=True,
                    ))
                    await session.commit()

    @staticmethod
    async def get_user_by_username(username: str):
        """
        Возвращает объект пользователя по его логину
        """
        async with get_session() as session:
            r = await session.execute(select(User).where(User.username == username))
        return r.scalar()

    @staticmethod
    async def get_admins() -> List[UserOut]:
        """
        Возвращает список всех администраторов
        """
        async with get_session() as session:
            admins = await session.execute(select(User).where(User.is_admin == True))
            return [UserOut(**admin.to_dict())
                    for admin in admins.scalars().all()]

    @staticmethod
    async def get_all_users(short_record=True) -> List[UserOut] | List[UserShort] | None:
        """
        Возвращает всех пользователей
        """
        async with get_session() as session:
            r = await session.execute(select(User))
            users = r.scalars().all()
            if users and short_record:
                return [UserShort(**user.to_dict())
                        for user in users]
            elif users:
                return [UserOut(**user.to_dict())
                        for user in users]
            return None

    @staticmethod
    async def add_user(user: UserWithPassword, is_admin=False) -> UserOut | None:
        """
        Добавляет нового администратора
        """
        async with get_session() as session:
            r = await session.execute(select(User).where(User.username == user.username))
            is_exist = r.scalar()
            if not is_exist:
                user.password = pwd_context.hash(user.password)
                session.add(User(is_admin=is_admin, **user.to_dict()))
                await session.commit()
                r = await session.execute(select(User).where(User.username == user.username))
                user = r.scalar()
                return UserOut(**user.to_dict())
            else:
                return None

    @staticmethod
    async def delete_user(idx: int) -> UserOut | None:
        """
        Удаление пользователя
        """
        async with get_session() as session:
            r = await session.execute(
                select(User).where(User.id == idx)
            )
            user = r.scalar()
            if user:
                r = await session.execute(
                    delete(User).where(User.id == idx)
                )
                return UserOut(**user.to_dict())
            else:
                return None

    @staticmethod
    async def edit_user(user: UserOut) -> UserOut | None:
        """
        Изменение пользователя
        """
        async with get_session() as session:
            r = await session.execute(
                select(User).where(User.id == user.id)
            )
            user_exists = r.scalar()
            if user_exists:
                r = await session.execute(
                    update(User).
                    where(User.id == user.id).
                    values(**user.to_dict())
                )
                return UserOut(**user.to_dict())
            else:
                return None

    @staticmethod
    async def change_password(idx: int, password: str):
        """Изменение пароля"""
        async with get_session() as session:
            password = pwd_context.hash(password)
            q = update(User).where(User.id == idx).values(password=password)
            await session.execute()
            await session.commit()

    @staticmethod
    async def run_cmd(idx: int, cmd: str) -> UserOut | None:
        """Выполняет быстрые команды: блокирование, разблокирование, выдача и удаление прав"""
        async with get_session() as session:
            r = await session.execute(select(User).where(User.id == idx))
            user = r.scalar()
            if user:
                if cmd == 'ban':
                    q = update(User).where(User.id == idx).values(disabled=True)
                elif cmd == 'unban':
                    q = update(User).where(User.id == idx).values(disabled=False)
                elif cmd == 'promote':
                    q = update(User).where(User.id == idx).values(is_admin=True)
                elif cmd == 'demote':
                    q = update(User).where(User.id == idx).values(is_admin=False)
                else:
                    return None

                await session.execute(q)
                await session.commit()

                r = await session.execute(select(User).where(User.id == idx))
                user = r.scalar()
                return UserOut(**user.to_dict())
            return None
