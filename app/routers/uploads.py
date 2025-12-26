from fastapi import APIRouter, UploadFile, Depends, HTTPException
from fastapi.responses import JSONResponse
from ..deps import get_historical_vote_service, get_current_user
import pandas as pd
from io import BytesIO, StringIO

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/votes-excel")
async def upload_votes_excel(file: UploadFile, svc = Depends(get_historical_vote_service)):
    try:
        if not file.filename.endswith((".xls", ".xlsx")):
            raise HTTPException(status_code=400, detail="Harus berupa file Excel (.xls atau .xlsx)")

        contents = await file.read()
        svc.import_votes_from_file(contents, filename=file.filename)
        return {"status":"ok", "message":"Imported votes"}
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
                "message": str(e) if e else "Terjadi kesalahan internal server"
            }
        )

# @router.post("/engagements-excel")
# Pending implementation for new Event structure
# async def upload_engagements_excel(...)

