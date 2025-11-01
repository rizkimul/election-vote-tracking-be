from fastapi import APIRouter, UploadFile, Depends, HTTPException
from ..deps import get_vote_service
import pandas as pd
from io import BytesIO

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/votes-excel")
async def upload_votes_excel(file: UploadFile, svc = Depends(get_vote_service)):
    if not file.filename.endswith((".xls", ".xlsx")):
        raise HTTPException(status_code=400, detail="Must be an Excel file (.xls or .xlsx)")

    contents = await file.read()
    try:
        df = pd.read_excel(BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse Excel: {str(e)}")

    # validate required columns
    required = {"district","sub_district","village","total_votes","election_year"}
    if not required.issubset(set(df.columns.str.lower())) and not required.issubset(set(df.columns)):
        # try lowercased columns: normalize
        df.columns = [c.lower() for c in df.columns]
    if not required.issubset(set(df.columns)):
        raise HTTPException(status_code=400, detail=f"Excel must contain columns: {required}")

    svc.import_votes_from_dataframe(df)
    return {"status":"ok", "message":"Imported votes"}
