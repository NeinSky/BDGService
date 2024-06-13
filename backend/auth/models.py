from pydantic import BaseModel
from typing import  Dict, Any
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserIn(BaseModel):
    username: str
    email: str | None = None
    full_name: str
    birthday: datetime

    def to_dict(self) -> Dict[str, Any]:
        return vars(self)


class UserOut(UserIn):
    id: int
    is_admin: bool
    disabled: bool


class UserWithPassword(UserIn):
    password: str


class UserShort(BaseModel):
    id: int
    email: str
    full_name: str
    birthday: datetime

    def to_dict(self) -> Dict[str, Any]:
        return vars(self)
