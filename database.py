from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import Base, Transport
import logging
from sqlite3 import IntegrityError


logger = logging.getLogger()

engine = create_engine("sqlite:///db.sqlite")

session = Session(engine, expire_on_commit=True, autoflush=False)


def db_init():
    Base.metadata.create_all(engine)


def create_transport(imei: str, name: str):
    try:
        with Session(engine, expire_on_commit=False) as session:
            transport = Transport(imei=imei, name=name)
            session.add(transport)
            session.commit()
            logger.info(f"Created Transport: {transport}")
            return transport
    except IntegrityError as e:
        logger.exception(f"Error while executing create_transport: {e}")


def get_all_transport():
    try:
        with Session(engine, expire_on_commit=False) as session:
            return session.scalars(select(Transport)).all()
    except Exception as e:
        logger.exception(f"Error while executing get_all_transport: {e}")
