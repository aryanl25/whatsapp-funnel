from typing import List, Dict, Any, Callable, Awaitable
from uuid import UUID
import time
from server.services.websocket_manager import manager
from server.schemas import (
    WebSocketEnvelope,
    WSMessageReceived,
    WSMessageSent,
    WSConversationUpdated,
    WSTakeoverStarted,
    WSTakeoverEnded,
    WSActionConversationsFlagged,
    WSActionHumanAttentionRequired,
    MessageOut,
    ConversationOut,
)
from server.enums import WSEvents, ConversationMode
from server.database import SessionLocal
from server.models import Conversation, User

# In-memory last seen for active users (for heartbeat)
last_seen: Dict[UUID, float] = {}

async def handle_heartbeat(user_id: UUID, payload: Dict[str, Any]):
    last_seen[user_id] = time.time()

async def handle_takeover_started(user_id: UUID, payload: Dict[str, Any]):
    conversation_id = payload.get("conversation_id")
    if not conversation_id:
        return

    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return

        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.organization_id == user.organization_id
        ).first()

        if not conversation:
            return

        # Update mode to HUMAN
        conversation.mode = ConversationMode.HUMAN
        # conversation.assigned_user_id = user_id # Optional assignment logic can be added here
        db.commit()
        db.refresh(conversation)

        # Broadcast update
        conv_out = ConversationOut.model_validate(conversation)
        await emit_conversation_updated(user.organization_id, conv_out)


async def handle_takeover_ended(user_id: UUID, payload: Dict[str, Any]):
    conversation_id = payload.get("conversation_id")
    if not conversation_id:
        return

    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return

        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.organization_id == user.organization_id
        ).first()

        if not conversation:
            return

        # Update mode back to BOT
        conversation.mode = ConversationMode.BOT
        db.commit()
        db.refresh(conversation)

        # Broadcast update
        conv_out = ConversationOut.model_validate(conversation)
        await emit_conversation_updated(user.organization_id, conv_out)

# Event Handler User Mapping
HANDLER_MAP: Dict[str, Callable[[UUID, Dict[str, Any]], Awaitable[None]]] = {
    WSEvents.CLIENT_HEARTBEAT: handle_heartbeat,
    WSEvents.TAKEOVER_STARTED: handle_takeover_started,
    WSEvents.TAKEOVER_ENDED: handle_takeover_ended,
}

async def handle_event(user_id: UUID, data: Dict[str, Any]):
    event_type = data.get("event")
    payload = data.get("payload", {})
    
    if event_type in HANDLER_MAP:
        await HANDLER_MAP[event_type](user_id, payload)
    else:
        # Optionally log unknown event or send error
        print(f"Unknown event received from {user_id}: {event_type}")

# Outbound Emitters
async def emit_conversation_updated(org_id: UUID, conversation: ConversationOut):
    payload = WSConversationUpdated(conversation=conversation)
    envelope = WebSocketEnvelope(event=WSEvents.CONVERSATION_UPDATED, payload=payload.model_dump())
    await manager.broadcast_to_org(org_id, envelope.model_dump())

async def emit_action_conversations_flagged(org_id: UUID, cta_id: UUID, conversation_ids: List[UUID]):
    payload = WSActionConversationsFlagged(cta_id=cta_id, conversation_ids=conversation_ids)
    envelope = WebSocketEnvelope(event=WSEvents.ACTION_CONVERSATIONS_FLAGGED, payload=payload.model_dump())
    await manager.broadcast_to_org(org_id, envelope.model_dump())

async def emit_action_human_attention_required(org_id: UUID, conversation_ids: List[UUID]):
    payload = WSActionHumanAttentionRequired(conversation_ids=conversation_ids)
    envelope = WebSocketEnvelope(event=WSEvents.ACTION_HUMAN_ATTENTION_REQUIRED, payload=payload.model_dump())
    await manager.broadcast_to_org(org_id, envelope.model_dump())