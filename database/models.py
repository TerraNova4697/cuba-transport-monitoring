from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base, engine


def db_init() -> None:
    """Create all tables."""
    Base.metadata.create_all(engine)


class Transport(Base):
    __tablename__ = "transports"

    imei: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now(), nullable=True)