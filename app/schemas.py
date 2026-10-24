"""Pydantic schemas: define what data the API ACCEPTS and RETURNS.
(Models = database shape, Schemas = API shape.)"""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------- Users ----------
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)  # bcrypt supports max 72 bytes


class AdminUserCreate(UserCreate):
    role: Literal["user", "admin"] = "user"


class UserUpdate(BaseModel):
    bio: Optional[str] = Field(default=None, max_length=300)
    username: Optional[str] = Field(default=None, min_length=3, max_length=30)


class UserPublic(BaseModel):
    """What other people can see on a profile page (no email!)."""
    model_config = ConfigDict(from_attributes=True)  # allow reading from DB objects
    id: int
    username: str
    bio: str
    created_at: datetime
    questions_count: int
    answers_count: int


class UserPrivate(UserPublic):
    """What the user sees about themselves (and admins see about everyone)."""
    email: EmailStr
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Answers ----------
class AnswerCreate(BaseModel):
    body: str = Field(min_length=3)


class AnswerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    body: str
    is_accepted: bool
    score: int
    author_name: str
    question_id: int
    created_at: datetime


class VoteIn(BaseModel):
    value: Literal[1, -1]  # only +1 or -1 is allowed


# ---------- Questions ----------
class QuestionCreate(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    body: str = Field(min_length=10)


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    body: str
    is_answered: bool
    author_name: str
    answers_count: int
    created_at: datetime


class QuestionDetail(QuestionOut):
    answers: list[AnswerOut]
