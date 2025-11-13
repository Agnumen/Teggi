from typing import List
from datetime import datetime
from sqlalchemy import (
    Enum as SqlEnum,
    text,
    func,
    TIMESTAMP,
    BigInteger,
    Boolean,
    
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from app.core.enums import UserRole


class User(Base):
    """Модель пользователя."""
    
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    
    role: Mapped[UserRole] = mapped_column(
        SqlEnum(UserRole),
        default=UserRole.USER,
        server_default=text("'USER'"),
    )
    
    notifications_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("'True'")
    )
    
    onboarding_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("'False'")
    )
    
    last_active: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    events: Mapped[List["Event"]] = relationship(  # noqa: F821  # type: ignore
        "Event",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    check_ins: Mapped[List["CheckIn"]] = relationship(  # noqa: F821 # type: ignore
        "CheckIn",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    activities: Mapped[List["Activity"]] = relationship(  # noqa: F821  # type: ignore
        "Activity",
        back_populates="user",
        cascade="all, delete-orphan"
    )

