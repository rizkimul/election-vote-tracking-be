from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from ..schemas import VoteCreate, VoteOut
from ..deps import get_vote_service, get_current_user
from typing import List, Optional

router = APIRouter(prefix="/votes", tags=["votes"])

@router.post("/", response_model=VoteOut)
def create_vote(payload: VoteCreate, svc = Depends(get_vote_service), user = Depends(get_current_user)):
    try:
        # user is available if you want to record who created the vote
        return svc.add_vote(payload)
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "status": e.status_code,
                "message": e.detail
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "message": str(e) if e else "Internal Server Error"
            }
        )

@router.get("/", response_model=List[VoteOut])
def list_votes(page: int = Query(1, ge=1),
               size: int = Query(20, ge=1, le=200),
               district: Optional[str] = None,
               sub_district: Optional[str] = None,
               village: Optional[str] = None,
               election_year: Optional[int] = None,
               svc = Depends(get_vote_service),
               user = Depends(get_current_user)):
    try:
        res = svc.list_votes(page=page, size=size, district=district, sub_district=sub_district, village=village, election_year=election_year)
        # return only items list to match response_model=List[VoteOut] OR return full meta — here we'll return items only
        return res["items"]
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "status": e.status_code,
                "message": e.detail
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "message": str(e) if e else "Internal Server Error"
            }
        )
