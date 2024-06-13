from fastapi import APIRouter
from typing import Annotated, List, Dict
from fastapi import Depends

from config import ALLOW_USER_REGISTRATION
from auth.auth import get_current_active_user
from auth.models import UserOut, UserWithPassword, UserShort
from database.models import User
from database.ext import subscribe as sub, unsubscribe as unsub, sub_list

from .status_codes import get_status_403_forbidden, get_status_400_bad_request, MSG_USER_EXISTS
router = APIRouter()


@router.post("/users/register")
async def register_user(user: UserWithPassword) -> UserOut:
    """
    Регистрация нового пользователя
    """
    if ALLOW_USER_REGISTRATION:
        new_user = await User.add_user(user)
        if new_user:
            return new_user
        get_status_400_bad_request(MSG_USER_EXISTS)
    get_status_403_forbidden()


@router.get("/users")
async def get_users(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> List[UserShort]:
    """
    Получение списка пользователей
    """
    return await User.get_all_users()


@router.get("/users/subscribe/list")
async def get_subscriptions(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> List[UserShort] | Dict:
    """
    Получение списка сотрудников, на которых подписан пользователей
    """
    subs = await sub_list(current_user.id)
    if subs:
        return subs
    return {'result': 'Вы пока ни на кого не подписаны'}


@router.get("/users/subscribe/{idx}")
async def subscribe(
    current_user: Annotated[User, Depends(get_current_active_user)],
    idx: int
) -> Dict:
    """
    Подписать на оповещение о дне рождения пользователя
    """
    error = await sub(current_user.id, idx)
    if not error:
        return {"result": "Успешно подписан!"}
    get_status_400_bad_request(error)


@router.get("/users/unsubscribe/{idx}")
async def unsubscribe(
    current_user: Annotated[User, Depends(get_current_active_user)],
    idx: int
) -> Dict:
    """
    Отписать от оповещений о дне рождения пользователя
    """
    error = await unsub(current_user.id, idx)
    if not error:
        return {"result": "Успешно отписан!"}
    get_status_400_bad_request(error)
