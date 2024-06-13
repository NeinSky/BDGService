from sqlalchemy import select, or_
from typing import List

from .connection import get_session
from .models import User, subscription as sub
from auth.models import UserShort

MSG_SUB_EXIST = "Подписка уже существует."
MSG_USERS_NOT_EXIST = "Одного или нескольких пользователей не удалось найти."
MSG_SUB_NOT_EXIST = "Подписка не существует"


async def subscribe(user_id: int, sub_id: int) -> None | str:
    """
    Функция, которая подписывает пользователя на рассылку

    :param user_id: id пользователя
    :param sub_id: id сотрудника на которого подписывается пользователь
    :return: None если всё прошло успешно, иначе сообщение ошибки
    """

    async with get_session() as session:
        q = select(User).where(or_(User.id == user_id, User.id == sub_id))
        r = await session.execute(q)
        users = r.scalars().all()
        if len(users) == 2:
            q = select(sub).where(sub.c.user_id == user_id, sub.c.sub_id == sub_id)
            r = await session.execute(q)
            sub_exists = r.scalar()
            if sub_exists:
                return MSG_SUB_EXIST
            new_sub = sub.insert().values(user_id=user_id, sub_id=sub_id)
            await session.execute(new_sub)
            await session.commit()
        else:
            return MSG_USERS_NOT_EXIST


async def unsubscribe(user_id: int, sub_id: int) -> None | str:
    """
    Функция, которая отписывает пользователя от рассылки

    :param user_id: id пользователя
    :param sub_id: id сотрудника от которого отписывается пользователь
    :return: None если всё прошло успешно, иначе сообщение ошибки
    """

    async with get_session() as session:
        q = select(sub).where(sub.c.user_id == user_id, sub.c.sub_id == sub_id)
        r = await session.execute(q)
        sub_exist = r.scalar()
        if sub_exist:
            q = sub.delete().where(sub.c.user_id == user_id, sub.c.sub_id == sub_id)
            await session.execute(q)
            await session.commit()
        else:
            return MSG_SUB_NOT_EXIST


async def sub_list(user_id: int) -> List[UserShort]:
    """
    Функция возвращает список сотрудников, на которых подписан пользователь
    """
    async with get_session() as session:
        q = select(User).join(sub, User.id == sub.c.sub_id).where(sub.c.user_id == user_id)
        r = await session.execute(q)
        result = r.scalars().all()
        return [UserShort(**user.to_dict())
                for user in result]
