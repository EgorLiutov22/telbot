from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True)
    first_name: Mapped[str] = mapped_column(String(30))
    messages: Mapped[List["Messages"]] = relationship(back_populates='user')


    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.first_name!r}, id={self.telegram_id})"


class Messages(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    user: Mapped["User"] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, text={self.text})"


