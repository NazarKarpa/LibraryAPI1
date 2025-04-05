from fastapi import FastAPI, Depends, Query
from fastapi.params import Depends
from pydantic import BaseModel, Field
from  typing import Union

from sqlalchemy.orm import Session
from db.database import SessionLocal, engine
from db import models, schemas, crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Залежність
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

all_books = {
    "Джордж Оруелл": [["1984", 328], ["Колгосп тварин", 112]],
    "Стівен Кінг": [["Воно", 1138], ["Сяйво", 447]],
    "Артур Конан Дойл": [["Пригоди Шерлока Холмса", 307], ["Собака Баскервілів", 256]],
    "Джоан Роулінг": [["Гаррі Поттер і філософський камінь", 223], ["Гаррі Поттер і таємна кімната", 251]],
    "Лев Толстой": [["Війна і мир", 1225], ["Анна Кареніна", 864]]
}


class Book(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=3, max_length=200)
    pages: int = Field(..., gt=10)



@app.get("/")
async def get_all_books(db: Session = Depends(get_db)):
    """return all books"""
    return crud.get_all_books(db)

@app.post('/add_book')
async def add_new_book(book: schemas.BookDB):
    """add new book"""
    if book.author not in all_books:
        all_books[book.author] = [[book.title], [book.pages]]
    else:
        all_books[book.author].append([book.title],[book.pages])

    return {"message": "Book created"}

@app.get("/author/{author}")
async  def get_author_books(author: str):
    if author in all_books:
        return all_books[author]
    else:
        return {"message": "Books not found"}

@app.put("/{author}/{book_title}")
async def update_book_pages(author: str, book_title: str,
                            new_pages: int = Query(gt=10, title='new page count',
                            description='new count pages in book')):
    if author in all_books:
        for book in all_books[author]:
            if book[0] == book_title:
                book[1] = new_pages
                return {'message': 'update count pages'}

    return {'error': 'not found'}


@app.delete('/{author}/{book_title}')
async def delete_book(author: str, book_title: str,):
    if author in all_books:
        for book in all_books[author]:
            if book[0] == book_title:
                all_books[author].remove(book)
                return {'message': 'success del'}

    return {'message': 'not found'}



