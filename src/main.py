from fastapi import FastAPI
from fastapi.responses import Response

from src.api.v1.endpoints import geolocations

from .database import engine
from .models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(geolocations.router, prefix="/geolocations", tags=["geolocations"])


@app.get("/")
def get_root():
    return Response(status_code=204)
