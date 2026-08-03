"""
User Pydantic Schemas
======================
Used for API request/response serialization.

TODO: Add UserUpdate schema, password change schema
"""

from pydantic import BaseModel, EmailStr
from enum import Enum


class UserRole(str, Enum):
    OPERATOR = "operator"
    MAINTENANCE = "maintenance"
    MANAGER = "manager"


class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = UserRole.OPERATOR


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
