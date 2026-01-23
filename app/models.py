# app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship, declarative_base
import enum
import datetime

Base = declarative_base()

class LabelStatus(str, enum.Enum):
    UNASSIGNED = "UNASSIGNED"
    PRINTED = "PRINTED"
    PLACED = "PLACED"
    RETIRED = "RETIRED"
    INVALIDATED = "INVALIDATED"

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    isbn = Column(String, nullable=True)

    labels = relationship("PaperLabel", back_populates="book")

class PaperLabel(Base):
    __tablename__ = "paper_labels"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    status = Column(Enum(LabelStatus), default=LabelStatus.UNASSIGNED)
    printed_at = Column(DateTime, nullable=True)
    invalidated_at = Column(DateTime, nullable=True)

    book = relationship("Book", back_populates="labels")