"""人物模块 Repository。"""

from __future__ import annotations

from app.models.person import FollowUpTask, ImportantDate, Person, PersonFact, Tag
from app.repositories.base import BaseRepository


class PersonRepository(BaseRepository[Person]):
    model = Person


class TagRepository(BaseRepository[Tag]):
    model = Tag


class PersonFactRepository(BaseRepository[PersonFact]):
    model = PersonFact


class ImportantDateRepository(BaseRepository[ImportantDate]):
    model = ImportantDate


class FollowUpRepository(BaseRepository[FollowUpTask]):
    model = FollowUpTask
