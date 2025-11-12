from fastapi import APIRouter, UploadFile, Depends, HTTPException
from fastapi.responses import JSONResponse
from ..deps import get_vote_service, get_engagement_service, get_current_user
import pandas as pd
from io import BytesIO, StringIO

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/votes-excel")
async def upload_votes_excel(file: UploadFile, svc = Depends(get_vote_service), user = Depends(get_current_user)):
    try:
        if not file.filename.endswith((".xls", ".xlsx")):
            raise HTTPException(status_code=400, detail="Must be an Excel file (.xls or .xlsx)")

        contents = await file.read()
        try:
            df = pd.read_excel(BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse Excel: {str(e)}")

        svc.import_votes_from_dataframe(df)
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
                "message": str(e) if e else "Internal Server Error"
            }
        )

@router.post("/engagements-excel")
async def upload_engagements_excel(file: UploadFile, svc = Depends(get_engagement_service), user = Depends(get_current_user)):
    try:
            
        # Accept Excel (.xls/.xlsx) or CSV
        filename = file.filename.lower()
        contents = await file.read()
        try:
            if filename.endswith((".xls", ".xlsx")):
                df = pd.read_excel(BytesIO(contents))
            elif filename.endswith(".csv"):
                df = pd.read_csv(StringIO(contents.decode('utf-8')))
            else:
                raise HTTPException(status_code=400, detail="File must be .xls, .xlsx or .csv")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

        try:
            svc.import_engagements_from_dataframe(df)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        return {"status":"ok", "message":"Imported engagements"}
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
