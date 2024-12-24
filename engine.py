from sqlalchemy import create_engine
from models import Base

engine = create_engine("sqlite:///db.sqlite", echo=True)  # создаем движок базы данных
Base.metadata.create_all(engine)  # создаем все таблицы, если не существуют
