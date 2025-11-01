from fastapi import APIRouter, Depends, HTTPException
from ..schemas import VoteCreate, VoteOut
from ..deps import get_vote_service
from typing import List

router = APIRouter(prefix="/votes", tags=["votes"])

@router.post("/", response_model=VoteOut)
def create_vote(payload: VoteCreate, svc = Depends(get_vote_service)):
    return svc.add_vote(payload)

@router.get("/", response_model=List[VoteOut])
def list_votes(svc = Depends(get_vote_service)):
    return svc.list_votes()
