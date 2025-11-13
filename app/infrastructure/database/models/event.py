from datetime import time, date
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Date,
    String,
    Time,
    text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Event(Base):
    """Модель события (элемента рутины)."""

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('users.user_id', ondelete="CASCADE")
    )
    
    event_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    
    name: Mapped[str] = mapped_column(String, nullable=False)
    event_date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    tag: Mapped[str] = mapped_column(String, nullable=False)
    
    status: Mapped[str] = mapped_column(
        String,
        default='pending',
        server_default=text("'pending'")
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="events",
    )