from pydantic import BaseModel
from typing import Optional

class BookOut(BaseModel):
    id: int
    title: str
    author: str
    isbn: Optional[str]

    class Config:
        orm_mode = True

class PaperLabelOut(BaseModel):
    paper_id: int
    book: BookOut
    status: str