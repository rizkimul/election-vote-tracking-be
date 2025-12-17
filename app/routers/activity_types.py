from fastapi import APIRouter, Depends, HTTPException
from ..schemas import ActivityTypeCreate, ActivityTypeOut
from ..deps import get_activity_type_service, get_current_user
from typing import List

router = APIRouter(prefix="/activity-types", tags=["activity-types"])

@router.post("/", response_model=ActivityTypeOut)
def create_activity_type(payload: ActivityTypeCreate, svc = Depends(get_activity_type_service), user = Depends(get_current_user)):
    return svc.create_activity_type(payload)

@router.get("/", response_model=List[ActivityTypeOut])
def list_activity_types(svc = Depends(get_activity_type_service), user = Depends(get_current_user)):
    return svc.list_activity_types()

@router.delete("/{activity_type_id}")
def delete_activity_type(activity_type_id: int, svc = Depends(get_activity_type_service), user = Depends(get_current_user)):
    return svc.delete_activity_type(activity_type_id)

