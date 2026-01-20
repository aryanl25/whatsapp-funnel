from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..models import CreditBalance, CreditTransaction, User
from ..schemas import CreditResponse, TransactionResponse
from ..dependencies import get_db

router = APIRouter()

@router.get("/", response_model=CreditResponse)
def get_credits(db: Session = Depends(get_db)):
    # Assuming one user/org for now, or get from current user
    balance_record = db.query(CreditBalance).first()
    if not balance_record:
        # Create a default balance if none exists
        balance_record = CreditBalance(balance=2500)
        db.add(balance_record)
        db.commit()
        db.refresh(balance_record)
    
    history = []
    for tx in balance_record.transactions:
        history.append(TransactionResponse(
            id=tx.id,
            type=tx.transaction_type,
            amount=tx.amount_currency or 0.0,
            credits=tx.credits_exchanged,
            date=tx.date
        ))
        
    return CreditResponse(
        balance=balance_record.balance,
        history=history
    )
