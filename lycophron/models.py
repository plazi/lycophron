from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///" + "data.db", echo=True)

session = sessionmaker()
session.configure(bind=engine)

Model = declarative_base()


class Record(Model):
    __tablename__ = "record"
    id = Column(Integer, primary_key=True)
    doi = Column(Integer)
    deposit_id = Column(Integer)


def create_all():
    Model.metadata.create_all(engine)
