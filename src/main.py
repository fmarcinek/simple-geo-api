import os

from fastapi import FastAPI
from fastapi.responses import Response

from src.api.v1.endpoints import geolocations

from .database import engine
from .models import Base

APP_NAME = "Simple Geo API"

Base.metadata.create_all(bind=engine)

app = (
    FastAPI(title=APP_NAME, docs_url=None, redoc_url=None)
    if os.getenv("APP_ENV") == "production"
    else FastAPI(title=APP_NAME)
)

app.include_router(geolocations.router, prefix="/geolocations", tags=["geolocations"])


@app.get("/")
def get_root():
    return Response(status_code=204)
