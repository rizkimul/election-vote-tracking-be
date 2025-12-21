from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from ..deps import get_prioritization_service, get_current_user
from ..services.prioritization_service import PrioritizationService

router = APIRouter(prefix="/prioritization", tags=["prioritization"])

@router.get("/suggest")
def get_prioritization_suggestions(svc: PrioritizationService = Depends(get_prioritization_service), user = Depends(get_current_user)):
    return svc.get_suggestions()
