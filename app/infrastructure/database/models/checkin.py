from datetime import datetime
from typing import TYPE_CHECKING, Dict, Any

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    String,
    TIMESTAMP,
    func
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User


class CheckIn(Base):
    """Модель чекина."""

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('users.user_id', ondelete="CASCADE"),
        nullable=False
    )
    
    timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )
    
    check_in_type: Mapped[str] = mapped_column(String, nullable=False)
    
    # Поле для хранения произвольных данных, например, {"feeling": "🙂"}
    data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)

    user: Mapped["User"] = relationship(
        "User",
        back_populates="check_ins",
    )