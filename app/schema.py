from pydantic import BaseModel, EmailStr, field_validator
from fastapi_users import schemas
import re
import uuid

class PostCreate(BaseModel):
    title: str
    content: str
    
class UserRead(schemas.BaseUser[uuid.UUID]):
    username: str

class UserUpdate(schemas.BaseUserUpdate):
    username: str | None = None

class UserCreate(schemas.BaseUserCreate):
    username: str
    email: EmailStr
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        # At least 8 chars, 1 uppercase, 1 lowercase, 1 number
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain a number')
        return v

