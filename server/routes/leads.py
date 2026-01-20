from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import SessionLocal
from ..models import Lead
from ..schemas import LeadCreate, LeadResponse, LeadUpdate
from ..dependencies import get_db

router = APIRouter()

@router.get("/", response_model=List[LeadResponse])
def get_leads(db: Session = Depends(get_db)):
    return db.query(Lead).all()

@router.post("/", response_model=LeadResponse)
def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    db_lead = Lead(**lead.model_dump(by_alias=False))
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: str, db: Session = Depends(get_db)):
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return db_lead

@router.patch("/{lead_id}", response_model=LeadResponse)
def update_lead(lead_id: str, lead: LeadUpdate, db: Session = Depends(get_db)):
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    update_data = lead.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_lead, key, value)
    
    db.commit()
    db.refresh(db_lead)
    return db_lead
