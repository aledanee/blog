from pydantic import BaseModel
from datetime import date
from typing import Optional


class User(BaseModel):
    username: str
    email: str
    password: str
    profile_picture: str


class UsereRgi(BaseModel):
    username: str
    email: str
    password: str
    profile_picture: Optional[str] = None

class Login(BaseModel):
    username: str
    password: str


class BlogPost(BaseModel):
    post_id: int
    title: str
    content: str
    publication_date: date
    author_id: int


class Like(BaseModel):
    post_id: int
    user_id: int


class Comment(BaseModel):
    post_id: int
    user_id: int
    comment_text: str
    comment_date: date

