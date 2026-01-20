from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..models import Template
from ..schemas import TemplateCreate, TemplateResponse
from ..dependencies import get_db

router = APIRouter()

@router.get("/", response_model=List[TemplateResponse])
def get_templates(db: Session = Depends(get_db)):
    return db.query(Template).all()

@router.post("/", response_model=TemplateResponse)
def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    db_template = Template(**template.model_dump(by_alias=False))
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(template_id: str, template: TemplateCreate, db: Session = Depends(get_db)):
    db_template = db.query(Template).filter(Template.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    for key, value in template.model_dump(by_alias=False).items():
        setattr(db_template, key, value)
    
    db.commit()
    db.refresh(db_template)
    return db_template

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(template_id: str, db: Session = Depends(get_db)):
    db_template = db.query(Template).filter(Template.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(db_template)
    db.commit()
    return None
