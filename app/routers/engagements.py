from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from ..schemas import EngagementCreate, EngagementOut
from ..deps import get_engagement_service, get_current_user
from typing import List, Optional
from datetime import date

router = APIRouter(prefix="/engagements", tags=["engagements"])

@router.post("/", response_model=EngagementOut)
def create_engagement(payload: EngagementCreate, svc = Depends(get_engagement_service), user = Depends(get_current_user)):
    return svc.add_engagement(payload)

@router.get("/", response_model=List[EngagementOut])
def list_engagements(page: int = Query(1, ge=1),
                     size: int = Query(20, ge=1, le=200),
                     district: Optional[str] = None,
                     event_type: Optional[str] = None,
                     date_from: Optional[date] = None,
                     date_to: Optional[date] = None,
                     min_participants: Optional[int] = None,
                     svc = Depends(get_engagement_service),
                     user = Depends(get_current_user)):
    try:
        res = svc.list_engagements(page=page, size=size, district=district, event_type=event_type, date_from=date_from, date_to=date_to, min_participants=min_participants)
        return res["items"]
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "status": e.status_code,
                "message": e.detail,
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "message": str(e) if e else "Internal Server Error",
            }
        )

@router.get("/heatmap")
def heatmap(svc = Depends(get_engagement_service), user = Depends(get_current_user)):
    return svc.heatmap()
