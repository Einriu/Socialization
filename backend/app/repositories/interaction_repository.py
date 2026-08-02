"""互动模块 Repository。"""

from __future__ import annotations

from app.models.interaction import Interaction
from app.repositories.base import BaseRepository


class InteractionRepository(BaseRepository[Interaction]):
    model = Interaction
