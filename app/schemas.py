from pydantic import BaseModel
from typing import Optional

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None

class BookOut(BaseModel):
    id: int
    title: str
    author: str
    isbn: Optional[str]

    class Config:
        orm_mode = True

class LabelMintRequest(BaseModel):
    book_id: int

class PaperLabelOut(BaseModel):
    id: int
    book: BookOut
    status: str

    class Config:
        orm_mode = True