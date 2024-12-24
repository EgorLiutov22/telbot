from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):  # наследуемся от DeclarativeBase, больше нужно для сокращения записи
    pass  # ничего не переопределяем


class User(Base):
    __tablename__ = "user_account"  # задаем имя таблицы в базе данных
    id: Mapped[int] = mapped_column(primary_key=True)  # id первичный ключ
    telegram_id: Mapped[int] = mapped_column(unique=True)  # id из телеграмма
    first_name: Mapped[str] = mapped_column(String(30))  # имя пользователя
    messages: Mapped[List["Messages"]] = relationship(back_populates='user')  # обратная связь с сообщениями

    # нужно на случай, если захотим посмотреть все сообщения пользователя

    def __repr__(self) -> str:
        # для вывода объекта в строковом виде при отладке
        return f"User(id={self.id!r}, name={self.first_name!r}, id={self.telegram_id})"


class Messages(Base):
    __tablename__ = "messages"  # задаем имя таблицы в базе данных
    id: Mapped[int] = mapped_column(primary_key=True)  # id первичный ключ
    text: Mapped[str]  # тект сообщения от пользователя
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))  # id пользователя, написавшего это сообщение
    user: Mapped["User"] = relationship(back_populates="messages")  # обратная связь с пользователем

    def __repr__(self) -> str:
        # для вывода объекта в строковом виде при отладке
        return f"Address(id={self.id!r}, text={self.text})"
