from fastapi import APIRouter, Depends, HTTPException, Query
from ..schemas import HistoricalVoteCreate, HistoricalVoteOut
from ..deps import get_historical_vote_service, get_current_user
from typing import List, Optional

router = APIRouter(prefix="/historical-votes", tags=["historical-votes"])

@router.post("/", response_model=HistoricalVoteOut)
def create_vote(payload: HistoricalVoteCreate, svc = Depends(get_historical_vote_service), user = Depends(get_current_user)):
    try:
        return svc.add_historical_vote(payload)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/filters")
def get_filters(dapil: Optional[str] = None, svc = Depends(get_historical_vote_service), user = Depends(get_current_user)):
    return svc.get_filter_options(dapil=dapil)

@router.get("/import-history")
def get_import_history(svc = Depends(get_historical_vote_service), user = Depends(get_current_user)):
    return svc.get_import_logs()


@router.get("/", response_model=List[HistoricalVoteOut])
def list_votes(page: int = Query(1, ge=1),
               size: int = Query(20, ge=1, le=2000),
               dapil: Optional[str] = None,
               kabupaten: Optional[str] = None,
               kecamatan: Optional[str] = None,
               desa: Optional[str] = None,
               election_year: Optional[int] = None,
               svc = Depends(get_historical_vote_service),
               user = Depends(get_current_user)):
    try:
        res = svc.list_historical_votes(page=page, size=size, dapil=dapil, kabupaten=kabupaten, kecamatan=kecamatan, desa=desa, election_year=election_year)
        return res["items"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
