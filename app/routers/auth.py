from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from ..schemas import UserCreate, UserOut, LoginSchema, UserUpdate, PasswordChange
from ..deps import get_auth_service, get_current_user
from ..models import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, auth_svc=Depends(get_auth_service)):
    try:
        new = auth_svc.register(user.username, user.name, user.password, user.nik)
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

@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserOut)
def update_profile(data: UserUpdate, current_user: User = Depends(get_current_user), auth_svc=Depends(get_auth_service)):
    try:
        updated_user = auth_svc.update_profile(current_user, data)
        return updated_user
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"status": e.status_code, "message": e.detail}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": 500, "message": str(e) if e else "Internal server error"}
        )

@router.put("/me/password")
def change_password(data: PasswordChange, current_user: User = Depends(get_current_user), auth_svc=Depends(get_auth_service)):
    try:
        auth_svc.change_password(current_user, data)
        return {"message": "Password berhasil diubah"}
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"status": e.status_code, "message": e.detail}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": 500, "message": str(e) if e else "Internal server error"}
        )

@router.post("/login")
def login(payload: LoginSchema, auth_svc=Depends(get_auth_service)):
    try:
            
        user = auth_svc.authenticate(payload.username, payload.password)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid credentials")
        # Use username as the token identifier, fallback to NIK for legacy users
        identifier = user.username or user.nik
        token = auth_svc.create_token(identifier)
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

