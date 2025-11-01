from fastapi import APIRouter, Depends
from ..schemas import EngagementCreate, EngagementOut
from ..deps import get_engagement_service
from typing import List

router = APIRouter(prefix="/engagements", tags=["engagements"])

@router.post("/", response_model=EngagementOut)
def create_engagement(payload: EngagementCreate, svc = Depends(get_engagement_service)):
    return svc.add_engagement(payload)

@router.get("/", response_model=List[EngagementOut])
def list_engagements(svc = Depends(get_engagement_service)):
    return svc.list_engagements()

@router.get("/heatmap")
def heatmap(svc = Depends(get_engagement_service)):
    return svc.heatmap()
