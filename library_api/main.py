import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.db import Base, engine
from api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    from models.library_models import Reservation, Book
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    lifespan=lifespan,
)

app.include_router(api_router, prefix='/api')

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
