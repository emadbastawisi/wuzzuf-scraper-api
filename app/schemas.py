from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, conint


class User(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserCreate(User):
    pass


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config():
        from_attributes = True


class login(BaseModel):
    email_or_username: str
    password: str


class keywords(BaseModel):
    keywords: str


class Out_Search_Keyword(BaseModel):
    user_id: int
    id: int
    keywords: str


class Job(BaseModel):
    title: str
    company: str
    location: str
    type: str
    skills: str
    link: str


class JobCreate(Job):
    created_at: datetime
    expired_at: datetime


class JobOut(Job):
    created_at: datetime

    class Config():
        from_attributes = True


class Url(BaseModel):
    url: str

# class PostBase(BaseModel):
#     title: str
#     content: str
#     published: bool = True

# class PostCreate(PostBase):
#     pass

# class Post(PostBase):
#     id: int
#     created_at: datetime
#     owner_id: int
#     owner: UserOut
#     class Config():
#         from_attributes = True

# class PostOut(BaseModel):
#     Post : Post
#     votes: int


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginOut(BaseModel):
    username: str
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str]

# class Vote(BaseModel):
#     post_id: int
#     dir: conint(le=1)
