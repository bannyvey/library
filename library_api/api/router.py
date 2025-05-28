from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from database.repositoryes import BookRepository, ReservationRepository

from schemes.v1 import (CreateBookSchema, ResponseBookSchema, ResponseReservationSchema, ListBook, BookSchema,
                        ReturnBookSchema)

api_router = APIRouter()


@api_router.post("/book", response_model=ResponseBookSchema)
async def create(book: CreateBookSchema, session: AsyncSession = Depends(get_db)):
    """
    Создает новую книгу в базе данных.
    """
    repo = BookRepository(session)
    db_book = await repo.create(
        title=book.title,
        author=book.author,
    )
    return db_book


@api_router.delete("/book/{book_id}/delete")
async def delete(book_id: int, session: AsyncSession = Depends(get_db)):
    """
    Удалить книгу
    """
    repo = BookRepository(session)
    await repo.delete(id_=book_id)
    return {"message": "Book deleted"}


@api_router.post("/book/{book_id}/borrow", response_model=ResponseBookSchema | ResponseReservationSchema)
async def borrow_book(book_id: int, user_id: str, session: AsyncSession = Depends(get_db)):
    """
    Взять книгу
    Если книга уже взята, происходит броинрование
    """
    repo_book = BookRepository(session)
    repo_reservation = ReservationRepository(session)

    book = await repo_book.get_first(id=book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book.user_id == user_id:
        raise HTTPException(status_code=403, detail="You already borrowed")

    active_reservation = await repo_reservation.get_first(book_id=book_id, user_id=user_id, status="pending")
    if active_reservation:
        raise HTTPException(status_code=400, detail="Book is already reserved")

    if book.is_borrowed:
        reservation = await repo_reservation.create(book_id=book_id, user_id=user_id, status="pending")
        return reservation
    else:
        result = await repo_book.update(id_=book_id, is_borrowed=True, user_id=user_id)
        return result


@api_router.get("/books", response_model=ListBook)
async def list_books(session: AsyncSession = Depends(get_db)):
    """Получение списка книг"""
    repo = BookRepository(session)
    books = await repo.list()
    return {"books": books}


@api_router.post("/book/{book_id}/return", response_model=ReturnBookSchema)
async def return_book(book_id: int, user_id: str, session: AsyncSession = Depends(get_db)):
    repo_reservation = ReservationRepository(session)
    repo_book = BookRepository(session)

    book = await repo_book.get_first(id=book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if not book.is_borrowed:
        raise HTTPException(status_code=400, detail="Book is not reserved")

    if book.user_id != user_id:
        raise HTTPException(status_code=403, detail="You are not the borrower")

    await repo_book.update(id_=book_id, is_borrowed=False, user_id=None)
    first_reservation = await repo_reservation.get_first(book_id=book_id, status="pending")

    next_user_id = None

    if first_reservation:
        next_user_id = first_reservation.user_id
        await repo_reservation.update(id_=first_reservation.id, status="fulfilled")
        await repo_book.update(id_=book_id, is_borrowed=True, user_id=next_user_id)
    updated_book = await repo_book.get_first(id=book_id)
    return {"book": updated_book, "user_id": next_user_id}
