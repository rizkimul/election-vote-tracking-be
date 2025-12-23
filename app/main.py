from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .database import engine
from . import models
from .routers import auth, events, uploads, activity_types  # historical_votes removed

# Create tables if you want (Alembic will handle migrations in production)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Election Vote Tracking API")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



app.include_router(auth.router)
# app.include_router(historical_votes.router)  # Removed: SABADESA doesn't use vote tracking
app.include_router(events.router)
app.include_router(activity_types.router)
app.include_router(uploads.router)
from .routers import analytics
app.include_router(analytics.router)
from .routers import prioritization
app.include_router(prioritization.router)

@app.get("/")
def home():
    return {"message":"Election API running"}

# --- Exception Handlers ---
from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import ResponseValidationError

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    # Parse error message to give user-friendly feedback
    error_info = str(exc.orig) if exc.orig else str(exc)
    
    if "unique constraint" in error_info.lower() or "unique" in error_info.lower():
        if "nik" in error_info.lower():
            return JSONResponse(
                status_code=400,
                content={"detail": "Gagal: NIK/NIS sudah terdaftar pada kegiatan ini."}
            )
        if "username" in error_info.lower():
            return JSONResponse(
                status_code=400,
                content={"detail": "Username sudah digunakan. Silakan pilih username lain."}
            )
            
    return JSONResponse(
        status_code=400,
        content={"detail": f"Terjadi kesalahan database: {error_info}"}
    )

@app.exception_handler(ResponseValidationError)
async def validation_exception_handler(request: Request, exc: ResponseValidationError):
    # This happens when backend data doesn't match Pydantic schema (e.g. null string)
    print(f"Validation Error: {exc}") # Log for dev
    return JSONResponse(
        status_code=500,
        content={"detail": "Terjadi kesalahan format data internal server."}
    )

