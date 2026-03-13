from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    role: str


class UserResponse(BaseModel):
    username: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
