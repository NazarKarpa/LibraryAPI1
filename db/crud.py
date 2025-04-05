from sqlalchemy.orm import Session
from . import models, schemas

def get_all_books(db:Session):
    books = db.query(models.Book).all()
    return books



