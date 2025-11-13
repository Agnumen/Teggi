from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional, Dict

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.infrastructure.database.models import User, CheckIn
# from app.core.schemas import UserCreateDTO, UserUpdateDTO
from app.core.enums import UserRole



class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    # async def create_user(self, user_id: int) -> User:
    #     user = User()
    #     self._session.add(user)
    #     await self._session.flush()
    #     return user
    
    async def get_or_create_user(self, user_id: int) -> User:
        """
        Получает пользователя по ID или создает нового, если он не найден.
        Обновляет время последней активности.
        """
        stmt = (
            pg_insert(User)
            .values(user_id=user_id, last_active=func.now())
            .on_conflict_do_update(
                index_elements=[User.user_id],
                set_={"last_active": func.now()}
            )
            .returning(User)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def delete_user(self, user_id: int):
        user = await self.get_by_id(user_id=user_id)
        if user:
            await self._session.delete(user)
    
    async def update_user_settings(self, user_id: int, key: str, value: Any) -> None:
        """Обновляет указанное поле в настройках пользователя."""
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values({key: value})
        )
        await self._session.execute(stmt)
    
    async def get_notifications_status_by_id(self, user_id: int) -> Optional[bool]:
        """Получает статус уведомлений по user_id"""
        stmt = (
            select(User.notifications_enabled)
            .filter(User.user_id == user_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def toggle_notifications(self, user_id: int) -> None:
        """Переключает статус уведомлений"""
        current = await self.get_notifications_status_by_id(user_id)
        
        new = not current
        
        await self.update_user_settings(user_id, User.notifications_enabled, new)
    
    
    async def get_user_role(self, user_id: int) -> Optional[UserRole]:
        stmt = (
            select(User.role)
            .filter(User.user_id == user_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def set_onboarding_complete(self, user_id: int) -> None:
        """Устанавливает флаг завершения онбординга для пользователя."""
        await self.update_user_settings(user_id, "onboarding_completed", True)

    async def get_all_user_ids(self) -> List[int]:
        """Возвращает список ID всех пользователей."""
        stmt = select(User.user_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_statistics(self) -> Dict[str, Any]:
        """Собирает и возвращает статистику по базе данных."""
        total_users_stmt = select(func.count(User.id))
        total_users = (await self._session.execute(total_users_stmt)).scalar_one()

        if total_users == 0:
            return {"error": "No users yet."}

        onboarded_users_stmt = select(func.count(User.id)).where(User.onboarding_completed)
        onboarded_users = (await self._session.execute(onboarded_users_stmt)).scalar_one()

        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        retention_stmt = select(func.count(User.id)).where(User.last_active > seven_days_ago)
        retention_7_days = (await self._session.execute(retention_stmt)).scalar_one()

        total_checkins_stmt = select(func.count(CheckIn.id))
        total_checkins = (await self._session.execute(total_checkins_stmt)).scalar_one()

        first_user_time_stmt = select(func.min(User.created_at))
        first_user_time = (await self._session.execute(first_user_time_stmt)).scalar_one()
        
        avg_checkins_per_day = 0
        if first_user_time.tzinfo is not None:
            first_user_date = first_user_time.astimezone(timezone.utc).date()
        else:
            first_user_date = first_user_time.date()
        
        current_date = datetime.now(timezone.utc).date()
        
        days_since_first_user = (current_date - first_user_date).days
        
        if days_since_first_user > 0:
            avg_checkins_per_day = total_checkins / days_since_first_user

        return {
            "total_users": total_users,
            "onboarding_completion_rate": (onboarded_users / total_users) * 100 if total_users > 0 else 0,
            "retention_7_days_count": retention_7_days,
            "total_checkins": total_checkins,
            "avg_checkins_per_day": avg_checkins_per_day,
        }