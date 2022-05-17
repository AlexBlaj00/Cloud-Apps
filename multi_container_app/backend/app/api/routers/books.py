from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
router = APIRouter(
    prefix='/api/books'
)
class Book(BaseModel):
    title: str
    author: str
all_books = [
    Book(title='Normal People', author='Sally Rooney'),
    Book(title='The Souls of Yellow Folk', author='Wesley Yang')
]
@router.get('/', response_model=List[Book])
async def get_books():
    '''
    Retrieve all books.
    '''
    return all_books
@router.get('/list/', response_model=List[str])
async def get_book_titles():
    '''
    Retrieve all book titles.
    '''
    return [book.title for book in all_books]