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
async def add_new_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    """add new book"""
    new_book = crud.create_book(book, db)
    return {"message": "Book created", 'book': new_book}

@app.get("/author/{author}")
async  def get_author_books(author: str, db: Session = Depends(get_db)):
    books = crud.get_books_by_author(author, db)
    if books:
        return books
    else:
        return {'message': 'this author nety'}


@app.put("/{author}/{book_title}")
async def update_book_pages(author: str,
                            title: str,
                            pages: int = Query(gt=10, title='new pages count'),
                            db: Session = Depends(get_db)):

    if crud.update_pages_book(author, title,  db):
        return {'message': 'Book was update'}
    return {'error': 'not found'}


@app.delete('/{author}/{book_title}')
async def delete_book(author: str, book_title: str, db: Session = Depends(get_db)):
    if crud.delete_book(author, book_title, db):
        return {'message': 'Book was deleted'}

    return {'message': 'not found'}



