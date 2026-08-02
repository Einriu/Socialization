"""ORM 模型统一导出（导入即注册全部元数据）。"""

from app.models.ai import AIModel, AIProvider, Conversation, ConversationLink, ConversationMessage
from app.models.base import Base
from app.models.interaction import Interaction, InteractionParticipant, InteractionTopic
from app.models.p1 import (
    AIUsageLog,
    ContextSnapshot,
    ConversationSummary,
    CustomField,
    CustomFieldValue,
    Document,
    DocumentChunk,
    DocumentLink,
    DocumentVersion,
    ProcessingJob,
)
from app.models.p2 import (
    InteractionExtractedFact,
    MemoryItem,
    PersonRelationship,
    PracticeEvaluation,
    PracticeMessage,
    PracticeScenario,
    PracticeSession,
    ReviewTask,
    TopicLearningRecord,
    UserProfile,
)
from app.models.person import FollowUpTask, ImportantDate, Person, PersonFact, PersonTag, Tag
from app.models.support import AppSetting, AuditLog, BackupRecord, PromptTemplate
from app.models.topic import Topic, TopicCategory, TopicNote, TopicPersonLink

__all__ = [
    "AIProvider",
    "AIModel",
    "AIUsageLog",
    "AppSetting",
    "AuditLog",
    "BackupRecord",
    "Base",
    "ContextSnapshot",
    "Conversation",
    "ConversationLink",
    "ConversationMessage",
    "ConversationSummary",
    "CustomField",
    "CustomFieldValue",
    "Document",
    "DocumentChunk",
    "DocumentLink",
    "DocumentVersion",
    "FollowUpTask",
    "ImportantDate",
    "Interaction",
    "InteractionParticipant",
    "InteractionTopic",
    "InteractionExtractedFact",
    "MemoryItem",
    "Person",
    "PersonFact",
    "PersonRelationship",
    "PersonTag",
    "PracticeEvaluation",
    "PracticeMessage",
    "PracticeScenario",
    "PracticeSession",
    "ProcessingJob",
    "PromptTemplate",
    "ReviewTask",
    "Tag",
    "Topic",
    "TopicCategory",
    "TopicLearningRecord",
    "TopicNote",
    "TopicPersonLink",
    "UserProfile",
]
