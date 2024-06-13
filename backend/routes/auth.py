from fastapi import APIRouter
from datetime import timedelta
from typing import Annotated, List, Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from auth.models import Token, UserOut, UserWithPassword
from auth.auth import authenticate_user, create_access_token, get_current_active_user
from database.models import User

from config import AUTH_ACCESS_TOKEN_EXPIRE_MINUTES
from .status_codes import get_status_403_forbidden, get_status_400_bad_request, MSG_USER_EXISTS, MSG_USER_NOT_FOUND

router = APIRouter()


@router.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=AUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


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


@router.post("/admins")
async def add_admin(
    current_user: Annotated[User, Depends(get_current_active_user)],
    admin: UserWithPassword
) -> UserOut | Dict:
    """
    Добавление администратора
    """
    if current_user.is_admin:
        admin = await User.add_user(admin, is_admin=True)
        if admin:
            return admin
        get_status_400_bad_request(MSG_USER_EXISTS)
    get_status_403_forbidden()


@router.post("/admins")
async def add_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    admin: UserWithPassword
) -> UserOut:
    """
    Добавление пользователя
    """
    if current_user.is_admin:
        admin = await User.add_user(admin, is_admin=True)
        if admin:
            return admin
        get_status_400_bad_request(MSG_USER_EXISTS)
    get_status_403_forbidden()


@router.delete("/admins/{idx}")
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


@router.patch('/admins')
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
