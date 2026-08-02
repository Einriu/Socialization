"""时间线服务（聚合互动/事实/重要日期）。"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.schemas.person import TimelineItem
from app.services.person_service import PersonService


class TimelineService:
    """时间线服务。"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.person_service = PersonService(db)

    def get_timeline(
        self, person_id: uuid.UUID, page: int, page_size: int
    ) -> tuple[list[TimelineItem], int]:
        return self.person_service.get_timeline(person_id, page, page_size)
