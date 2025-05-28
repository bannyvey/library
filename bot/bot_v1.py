import asyncio

from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.filters import Command
import httpx


TOKEN = ""
API_URL = "http://localhost:8000/api"

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def check_book_id(message: Message, args: list['str'], command: str) -> int | None:
    """Извлекает и проверяет book_id из аргументов команды."""
    if not args:
        await message.reply(f"Использование: {command} <id_книги>")
        return None
    try:
        return int(args[0])
    except ValueError:
        await message.reply("ID книги должен быть числом")
        return


async def make_api_request(message: Message, method: str, url: str, **kwargs) -> dict | None:
    """Универсальная функция для выполнения HTTP-запросов."""
    async with httpx.AsyncClient() as client:
        try:
            response = await getattr(client, method)(url, **kwargs)
            if response.status_code == 200:
                return response.json()
            else:
                detail = response.json().get("detail", "Неизвестная ошибка")
                await message.reply(f"Ошибка: {detail}")
        except httpx.RequestError:
            await message.reply("Ошибка соединения с сервером")


@dp.message(Command("start"))
async def start(message: Message):
    await message.reply(
        "Добро пожаловать в библиотеку!\n"
        "Команды:\n"
        "/add <название> <автор> — Добавить книгу\n"
        "/delete <id_книги> — Удалить книгу\n"
        "/list — Показать все книги\n"
        "/borrow <id_книги> — Взять или забронировать книгу\n"
        "/return <id_книги> - Вернуть книгу"
    )


@dp.message(Command("add"))
async def add_book(message: Message):
    args = message.text.split()[1:]
    if len(args) < 2:
        await message.reply("Использование: /add <название> <автор>")
        return
    title = " ".join(args[:-1])
    author = args[-1]
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_URL}/book", json={"title": title, "author": author})
        if response.status_code == 200:
            await message.reply(f"Книга '{title}' от {author} добавлена!")
        else:
            await message.reply(f"Книга не лобавлена")


@dp.message(Command("delete"))
async def delete_book(message: Message):
    args = message.text.split()[1:]
    book_id = await check_book_id(message, args, "/delete")
    if book_id is None:
        return
    data = await make_api_request(message, "delete", f"{API_URL}/book/{book_id}/delete")
    if data:
        await message.reply("Книга удалена!")


@dp.message(Command("list"))
async def list_books(message: Message):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/books")
        if response.status_code == 200:
            books = response.json()
            if not books:
                await message.reply("Библиотека пуста!")
                return
            response_text = "Список книг:\n"
            for book in books['books']:
                status = "Занята" if book['is_borrowed'] else "Доступна"
                response_text += f"ID: {book["id"]}, Название: {book["title"]}, Автор: {book["author"]}, Статус: {status}\n"
            await message.reply(response_text)
        else:
            await message.reply("Ошибка при получении списка книг")


@dp.message(Command("borrow"))
async def borrow_book(message: Message):
    args = message.text.split()[1:]
    book_id = await check_book_id(message, args, "/borrow")
    if book_id is None:
        return
    user_id = str(message.from_user.id)

    data = await make_api_request(message, "post", f"{API_URL}/book/{book_id}/borrow", params={
        "user_id": user_id
    })
    if data is not None:
        if "status" in data:
            await message.reply(f"Книга зарезервирована! ID брони: {data['id']}")
        elif "title" in data:
            await message.reply(f"Книга '{data['title']}' взята!")


@dp.message(Command("return"))
async def return_book(message: Message):
    args = message.text.split()[1:]
    book_id = await check_book_id(message, args, "/return")
    if book_id is None:
        return
    user_id = str(message.from_user.id)
    data = await make_api_request(
        message,
        "post",
        f"{API_URL}/book/{book_id}/return", params={"user_id": user_id}
    )
    if data:
        await message.reply(f"Вы успешно вернули книгу: {data['book']['title']}")
        if data['user_id']:
            await bot.send_message(
                chat_id=data['user_id'],
                text=f"Книга '{data['book']['title']}' теперь доступна. Вы можете её забрать!"
            )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
