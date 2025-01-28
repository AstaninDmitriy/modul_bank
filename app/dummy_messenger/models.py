import uuid
from datetime import datetime
import sqlalchemy
from sqlalchemy import DateTime, func, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import (
    DeclarativeBase, declarative_mixin, Mapped, mapped_column
    )

metadata = sqlalchemy.MetaData()


@declarative_mixin
class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


@declarative_mixin
class TimestampMixin:
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=datetime.now(),
    )


class Base(TimestampMixin, UUIDMixin, DeclarativeBase):
    metadata = metadata


class UserMessages(Base):
    __tablename__ = "user_messages"

    message: Mapped[str] = mapped_column(String(1024), nullable=False)

    user_name: Mapped[str] = mapped_column(String(64), nullable=False)
