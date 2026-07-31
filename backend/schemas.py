from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

# ==========================
# User Schemas
# ==========================

class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# ==========================
# Note Schemas
# ==========================

class NoteBase(BaseModel):
    title: str
    content: str
    tags: Optional[str] = None


class NoteCreate(NoteBase):
    user_id: int


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[str] = None


class NoteResponse(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int

    model_config = ConfigDict(from_attributes=True)