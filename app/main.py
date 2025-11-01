from fastapi import FastAPI
from .database import engine
from . import models
from .routers import auth, votes, engagements, uploads

# Create tables if you want (Alembic will handle migrations in production)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Election Vote Tracking API - Service/Repository (Sync)")

app.include_router(auth.router)
app.include_router(votes.router)
app.include_router(engagements.router)
app.include_router(uploads.router)

@app.get("/")
def home():
    return {"message":"Election API running"}

