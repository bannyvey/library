from datetime import datetime
from typing import List
from sqlalchemy import String, Boolean, Integer, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base


class Book(Base):
    __tablename__ = 'book_table'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(30))
    author: Mapped[str] = mapped_column(String(30))
    is_borrowed: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[str] = mapped_column(String(30), nullable=True)
    reservations: Mapped[List["Reservation"]] = relationship(
        back_populates="book",
        cascade="all, delete-orphan"
    )


class Reservation(Base):
    __tablename__ = 'reservations_table'
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey('book_table.id'), nullable=False)
    user_id: Mapped[str] = mapped_column(String(30))
    create_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    status: Mapped[str] = mapped_column(String(20), default="pending")  # "pending", "canceled", "fulfilled"
    book: Mapped["Book"] = relationship(back_populates="reservations")

