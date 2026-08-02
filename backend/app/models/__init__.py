"""ORM 模型统一导出（导入即注册全部元数据）。"""

from app.models.ai import AIModel, AIProvider, Conversation, ConversationLink, ConversationMessage
from app.models.base import Base
from app.models.interaction import Interaction, InteractionParticipant, InteractionTopic
from app.models.person import FollowUpTask, ImportantDate, Person, PersonFact, PersonTag, Tag
from app.models.support import AppSetting, AuditLog, BackupRecord, PromptTemplate
from app.models.topic import Topic, TopicCategory, TopicNote, TopicPersonLink

__all__ = [
    "AIProvider",
    "AIModel",
    "AppSetting",
    "AuditLog",
    "BackupRecord",
    "Base",
    "Conversation",
    "ConversationLink",
    "ConversationMessage",
    "FollowUpTask",
    "ImportantDate",
    "Interaction",
    "InteractionParticipant",
    "InteractionTopic",
    "Person",
    "PersonFact",
    "PersonTag",
    "PromptTemplate",
    "Tag",
    "Topic",
    "TopicCategory",
    "TopicNote",
    "TopicPersonLink",
]
