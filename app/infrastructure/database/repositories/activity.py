from typing import List, Any, Optional

from sqlalchemy import select, func, desc
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.models import Activity

class ActivityRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
        
    async def add_user_activity(self, user_id: int) -> None:
        stmt = (
            pg_insert(Activity)
            .values(user_id=user_id)
            .on_conflict_do_update(
                index_elements=["user_id", "activity_date"],
                set_={'actions': Activity.actions + 1}
            )
        )
        await self._session.execute(stmt)
        
    async def get_statistics(self) -> Optional[List[tuple[Any, ...]]]:
        stmt = (
            select(Activity.user_id, func.sum(Activity.actions).label("total"))
            .group_by(Activity.user_id)
            .order_by(desc("total"))
            .limit(5)
        )
        result = await self._session.execute(stmt)
        return result.all()
    
"""
add_user_activity
get_statistics
"""