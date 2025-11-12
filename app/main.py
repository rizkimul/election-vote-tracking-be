from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .database import engine
from . import models
from .routers import auth, votes, engagements, uploads

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

@app.middleware("http")
async def catch_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

app.include_router(auth.router)
app.include_router(votes.router)
app.include_router(engagements.router)
app.include_router(uploads.router)

@app.get("/")
def home():
    return {"message":"Election API running"}

