from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str  # worker, manager, factory_admin, buyer, platform_admin
    factory_id: Optional[int] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    factory_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
