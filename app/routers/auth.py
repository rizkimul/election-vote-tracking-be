from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from ..schemas import UserCreate, UserOut, LoginSchema
from ..deps import get_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, auth_svc=Depends(get_auth_service)):
    try:
        new = auth_svc.register(user.nik, user.name, user.password)
        return new
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
                "message": str(e) if e else "Internal server error",
            }
        )

@router.post("/login")
def login(payload: LoginSchema, auth_svc=Depends(get_auth_service)):
    try:
            
        user = auth_svc.authenticate(payload.nik, payload.password)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid credentials")
        token = auth_svc.create_token(user.nik)
        return token
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
                "message": str(e) if e else "Internal server error",
            }
        )
