from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class CreateBookSchema(BaseModel):
    title: str
    author: str


class ResponseBookSchema(BaseModel):
    title: str
    author: str
    is_borrowed: bool


class ResponseReservationSchema(BaseModel):
    id: int
    book_id: int
    user_id: str
    create_at: datetime
    status: str


class BookSchema(BaseModel):
    id: int
    title: str
    author: str
    is_borrowed: bool


class ListBook(BaseModel):
    books: List[BookSchema]


class ReturnBookSchema(BaseModel):
    book: BookSchema
    user_id: Optional[str]
