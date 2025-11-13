from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import CheckIn


class CheckInRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save_check_in(self, user_id: int, check_in_type: str, data: Dict[str, Any]) -> None:
        """Сохраняет новый чекин в базу данных."""
        check_in = CheckIn(
            user_id=user_id,
            check_in_type=check_in_type,
            data=data
        )
        self._session.add(check_in)
        await self._session.flush()