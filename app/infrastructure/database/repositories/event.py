import time
import random
from datetime import datetime as dt, date
from typing import List, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import Event


class EventRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def add_event(self, user_id: int, name: str, start_time: str, end_time: str, tag: str, event_date: date = date.today()) -> str:
        """Добавляет новое событие для пользователя."""
        
        unique_part = f"{int(time.time() * 1000)}_{random.randint(100, 999)}" 
        # Note: we dont need uuid because it will cause problems with callback data. 
         
        event_id = f"evt_{user_id}_{unique_part}"

        start_time_obj = dt.strptime(start_time, '%H:%M').time()
        end_time_obj = dt.strptime(end_time, '%H:%M').time()

        event = Event(
            event_id=event_id,
            user_id=user_id,
            name=name or "Не указано",
            start_time=start_time_obj,
            end_time=end_time_obj,
            event_date=event_date or dt.now().date(),
            tag=tag,
            status="pending"
        )
        self._session.add(event)
        await self._session.flush()
        return event.event_id
    
    async def get_user_events(self, user_id: int, event_date: date=date.today()) -> List[Event]:
        """Возвращает все события пользователя, отсортированные по времени начала."""
        stmt = (
            select(Event)
            .where(Event.user_id == user_id, Event.event_date == event_date)
            .order_by(Event.start_time)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Возвращает одно событие по его ID."""
        stmt = select(Event).where(Event.event_id == event_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_event(self, event_id: str) -> bool:
        """Удаляет событие по ID и возвращает True в случае успеха."""
        stmt = delete(Event).where(Event.event_id == event_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def clear_user_routine(self, user_id: int) -> int:
        """Удаляет все события пользователя и возвращает количество удаленных."""
        stmt = delete(Event).where(Event.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.rowcount