from enum import Enum

class ConversationStage(str, Enum):
    GREETING = "greeting"
    QUALIFICATION = "qualification"
    PRICING = "pricing"
    CTA = "cta"
    FOLLOWUP = "followup"
    CLOSED = "closed"
    LOST = "lost"
    GHOSTED = "ghosted"

class IntentLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    UNKNOWN = "unknown"

class CTAType(str, Enum):
    BOOK_CALL = "book_call"
    BOOK_DEMO = "book_demo"
    BOOK_MEETING = "book_meeting"
    

class ConversationMode(str, Enum):
    BOT = "bot"
    HUMAN = "human"
    CLOSED = "closed"
    PAUSED = "paused"

class UserSentiment(str, Enum):
    ANNOYED = "annoyed"
    DISTRUSTFUL = "distrustful"
    CONFUSED = "confused"
    CURIOUS = "curious"
    DISAPPOINTED = "disappointed"
    NEUTRAL = "neutral"
    UNINTERESTED = "uninterested"

class TemplateStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class MessageFrom(str, Enum):
    LEAD = "lead"
    BOT = "bot"
    HUMAN = "human"
