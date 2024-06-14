from fastapi import APIRouter
from typing import Annotated, List, Dict
from fastapi import Depends

from .models import UserOut, UserWithPassword
from config import AUTH_PASSWORD_MIN_LENGTH
from auth.auth import get_current_active_user
from database.models import User

from .status_codes import (get_status_403_forbidden, get_status_400_bad_request,
                           MSG_USER_EXISTS, MSG_USER_NOT_FOUND, MSG_PASSWORD_TOO_SHORT)

router = APIRouter()


@router.get("/admins")
async def get_admins(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> List[UserOut]:
    """
    Получение списка администраторов
    """
    if current_user.is_admin:
        return await User.get_admins()
    get_status_403_forbidden()


@router.post("/admins/users")
async def add_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    user: UserWithPassword
) -> UserOut | Dict:
    """
    Добавление администратора
    """
    if current_user.is_admin:
        if len(user.password) >= AUTH_PASSWORD_MIN_LENGTH:
            user = await User.add_user(user)
            if user:
                return user
            get_status_400_bad_request(MSG_USER_EXISTS)
        else:
            get_status_400_bad_request(MSG_PASSWORD_TOO_SHORT.format(AUTH_PASSWORD_MIN_LENGTH))
    get_status_403_forbidden()


@router.delete("/admins/users/{idx}")
async def delete_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    idx: int
) -> UserOut:
    """
    Удаление пользователя
    """
    if current_user.is_admin:
        user = await User.delete_user(idx)
        if user:
            return user
        get_status_400_bad_request(MSG_USER_NOT_FOUND)
    get_status_403_forbidden()


@router.patch('/admins/users')
async def edit_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    user: UserOut
) -> UserOut | None:
    """
    Изменение пользователя
    """
    if current_user.is_admin:
        user = await User.edit_user(user)
        if user:
            return user
        get_status_400_bad_request(MSG_USER_NOT_FOUND)
    get_status_403_forbidden()


@router.patch('/admins/users/ban/{idx}')
async def ban_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    idx: int
) -> UserOut:
    """
    Заблокировать пользователя
    """
    if current_user.is_admin:
        user = await User.run_cmd(idx, cmd="ban")
        if user:
            return user
        get_status_400_bad_request(MSG_USER_NOT_FOUND)
    get_status_403_forbidden()


@router.patch('/admins/users/unban/{idx}')
async def ban_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    idx: int
) -> UserOut:
    """
    Разблокировать пользователя
    """
    if current_user.is_admin:
        user = await User.run_cmd(idx, cmd="unban")
        if user:
            return user
        get_status_400_bad_request(MSG_USER_NOT_FOUND)
    get_status_403_forbidden()


@router.patch('/admins/users/promote/{idx}')
async def promote_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    idx: int
) -> UserOut:
    """
    Сделать пользователя администратором
    """
    if current_user.is_admin:
        user = await User.run_cmd(idx, cmd="promote")
        if user:
            return user
        get_status_400_bad_request(MSG_USER_NOT_FOUND)
    get_status_403_forbidden()


@router.patch('/admins/users/demote/{idx}')
async def demote_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    idx: int
) -> UserOut:
    """
    Сделать отнять права администратора
    """
    if current_user.is_admin:
        user = await User.run_cmd(idx, cmd="demote")
        if user:
            return user
        get_status_400_bad_request(MSG_USER_NOT_FOUND)
    get_status_403_forbidden()
