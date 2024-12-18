from sqlalchemy import select

from database.database import session_maker
from database.models import Transport
from logger import logger
from sqlite3 import IntegrityError


class TransportOrm:

    @staticmethod
    def create_transport(imei: str, name: str) -> Transport:
        """Create Transport and return new instance of Transport.

        Args:
            imei (str): Tracker IMEI.
            name (str): Transport name.

        Returns:
            Transport: Transport instance.
        """
        try:
            with session_maker() as session:
                transport = Transport(
                    imei=imei, name=name
                )
                session.add(transport)
                session.commit()
                return transport
        except IntegrityError as e:
            logger.exception(e)

    @staticmethod
    def get_all_transport() -> list[Transport]:
        try:
            with session_maker() as session:
                query = (
                    select(Transport)
                )
                return session.execute(query).scalars().all()
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def update_transport(transport: Transport):
        try:
            with session_maker() as session:
                session.add(transport)
                session.commit()
        except IntegrityError as e:
            logger.exception(e)
