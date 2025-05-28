from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository(ABC):
    @abstractmethod
    def get_first(self, **kwargs):
        pass

    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def create(self, **kwargs):
        pass

    @abstractmethod
    def update(self, **kwargs):
        pass

    @abstractmethod
    def delete(self, *args):
        pass


T = TypeVar('T')


class SQLAlchemyRepository(BaseRepository, Generic[T]):
    model: T = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_first(self, **kwargs) -> T:
        result = await self.session.scalars(select(self.model).filter_by(**kwargs))
        return result.first()

    async def list(self) -> Sequence[T]:
        result = await self.session.scalars(select(self.model))
        return result.all()

    async def create(self, **kwargs) -> T:
        result = self.model(**kwargs)
        self.session.add(result)
        await self.session.commit()
        await self.session.refresh(result)
        return result

    async def update(self, id_: int, **kwargs) -> T:
        result = await self.session.scalars(select(self.model).where(self.model.id == id_))
        obj = result.first()

        for key, value in kwargs.items():
            setattr(obj, key, value)

        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete(self, id_: int) -> None:
        result = await self.session.scalars(select(self.model).where(self.model.id == id_))
        obj = result.first()
        await self.session.delete(obj)


