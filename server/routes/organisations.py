from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from server.schemas import OrganisationResponse, RoleAssignment
from server.models import Organisation, UserRole
from server.dependencies import get_db, get_current_user, get_current_user_with_role
from server.permissions import can_assign_roles, check_org_access
from typing import List
from server.models import User

router = APIRouter()

# =========================================================
# ORGANISATION ENDPOINTS
# =========================================================
@router.get("/{org_id}", response_model=OrganisationResponse)
def get_organisation(
    org_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify user belongs to this org
    if current_user.org_id != org_id:
        raise HTTPException(status_code=403, detail="Access denied: not a member of this organisation")
    
    org = db.query(Organisation).filter(Organisation.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    
    return org
