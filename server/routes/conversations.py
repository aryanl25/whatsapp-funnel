from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..models import Conversation, Message
from ..schemas import ConversationResponse
from ..dependencies import get_db

router = APIRouter()

@router.get("/", response_model=List[ConversationResponse])
def get_conversations(db: Session = Depends(get_db)):
    return db.query(Conversation).all()

@router.get("/{lead_id}", response_model=ConversationResponse)
def get_conversation_by_lead(lead_id: str, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.lead_id == lead_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found for this lead")
    return conv
