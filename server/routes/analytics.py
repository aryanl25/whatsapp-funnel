from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Lead, Conversation, Campaign, Template
from ..schemas import AnalyticsResponse, SentimentStats, TemplateStats
from ..dependencies import get_db
from ..enums import LeadStage

router = APIRouter()

@router.get("/", response_model=AnalyticsResponse)
def get_analytics(db: Session = Depends(get_db)):
    active_convs = db.query(Conversation).filter(Conversation.bot_active == True).count()
    positive_leads = db.query(Lead).filter(Lead.stage.in_([LeadStage.CONTACTED, LeadStage.DEMO_SCHEDULED, LeadStage.QUALIFIED])).count()
    total_leads = db.query(Lead).count()
    
    conversion_rate = (positive_leads / total_leads * 100) if total_leads > 0 else 0.0
    
    # Sentiment is not yet stored in models, returning dummy for now as per mock
    sentiment = SentimentStats(positive=30, neutral=45, negative=25)
    
    # Template stats
    templates = db.query(Template).all()
    template_stats = []
    for t in templates:
        # In a real app, we'd query a MessageLog table for these stats
        template_stats.append(TemplateStats(
            id=t.id,
            sent=120, # Dummy
            clicks=15, # Dummy
            conversion=6.0 # Dummy
        ))
    
    return AnalyticsResponse(
        activeConversations=active_convs,
        positiveLeads=positive_leads,
        conversionRate=conversion_rate,
        sentiment=sentiment,
        templates=template_stats
    )
