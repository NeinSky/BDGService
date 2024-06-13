from fastapi import APIRouter
from datetime import timedelta
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict

from auth.auth import authenticate_user, create_access_token, get_current_active_user
from config import ALLOW_USER_REGISTRATION, AUTH_PASSWORD_MIN_LENGTH
from database.models import User
from .models import Token, UserOut, UserWithPassword
from .status_codes import get_status_400_bad_request, get_status_403_forbidden, MSG_USER_EXISTS, MSG_PASSWORD_TOO_SHORT

from config import AUTH_ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()


@router.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    Авторизация пользователя и получение токена
    """
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


@router.post("/register")
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


@router.patch("/change_password")
async def change_password(
    current_user: Annotated[User, Depends(get_current_active_user)],
    password: str
) -> Dict:
    """
    Смена пароля
    """
    if len(password) >= AUTH_PASSWORD_MIN_LENGTH:
        await User.change_password(current_user.id, password)
        return {"result": "Пароль изменён"}
    get_status_400_bad_request(MSG_PASSWORD_TOO_SHORT.format(AUTH_PASSWORD_MIN_LENGTH))
