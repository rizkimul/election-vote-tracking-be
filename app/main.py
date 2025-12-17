from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .database import engine
from . import models
from .routers import auth, historical_votes, events, uploads, activity_types

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
app.include_router(historical_votes.router)
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

