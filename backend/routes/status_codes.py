from fastapi import HTTPException, status

MSG_USER_NOT_FOUND = "Пользователь не найден"
MSG_USER_EXISTS = "Пользователь уже существует"
MSG_DEFAULT = "Неверный запрос"


def get_status_403_forbidden():
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Недостаточно прав",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_status_400_bad_request(message: str = MSG_DEFAULT):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )
