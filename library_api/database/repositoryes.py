from models.library_models import Reservation, Book
from database.base_repository import SQLAlchemyRepository


class BookRepository(SQLAlchemyRepository[Book]):
    model = Book


class ReservationRepository(SQLAlchemyRepository[Reservation]):
    model = Reservation
