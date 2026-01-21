from typing import List
from uuid import UUID
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
from server.enums import WSEvents


async def emit_message_received(org_id: UUID, message: MessageOut):
    payload = WSMessageReceived(message=message)
    envelope = WebSocketEnvelope(event=WSEvents.MESSAGE_RECEIVED, payload=payload.model_dump())
    await manager.broadcast_to_org(org_id, envelope.model_dump())


async def emit_message_sent(org_id: UUID, message: MessageOut):
    payload = WSMessageSent(message=message)
    envelope = WebSocketEnvelope(event=WSEvents.MESSAGE_SENT, payload=payload.model_dump())
    await manager.broadcast_to_org(org_id, envelope.model_dump())


async def emit_conversation_updated(org_id: UUID, conversation: ConversationOut):
    payload = WSConversationUpdated(conversation=conversation)
    envelope = WebSocketEnvelope(event=WSEvents.CONVERSATION_UPDATED, payload=payload.model_dump())
    await manager.broadcast_to_org(org_id, envelope.model_dump())


async def emit_takeover_started(org_id: UUID, conversation_id: UUID, assigned_user_id: UUID):
    payload = WSTakeoverStarted(conversation_id=conversation_id, assigned_user_id=assigned_user_id)
    envelope = WebSocketEnvelope(event=WSEvents.TAKEOVER_STARTED, payload=payload.model_dump())
    await manager.broadcast_to_org(org_id, envelope.model_dump())


async def emit_takeover_ended(org_id: UUID, conversation_id: UUID):
    payload = WSTakeoverEnded(conversation_id=conversation_id)
    envelope = WebSocketEnvelope(event=WSEvents.TAKEOVER_ENDED, payload=payload.model_dump())
    await manager.broadcast_to_org(org_id, envelope.model_dump())


async def emit_action_conversations_flagged(org_id: UUID, cta_id: UUID, conversation_ids: List[UUID]):
    payload = WSActionConversationsFlagged(cta_id=cta_id, conversation_ids=conversation_ids)
    envelope = WebSocketEnvelope(event=WSEvents.ACTION_CONVERSATIONS_FLAGGED, payload=payload.model_dump())
    await manager.broadcast_to_org(org_id, envelope.model_dump())


async def emit_action_human_attention_required(org_id: UUID, conversation_ids: List[UUID]):
    payload = WSActionHumanAttentionRequired(conversation_ids=conversation_ids)
    envelope = WebSocketEnvelope(event=WSEvents.ACTION_HUMAN_ATTENTION_REQUIRED, payload=payload.model_dump())
    await manager.broadcast_to_org(org_id, envelope.model_dump())