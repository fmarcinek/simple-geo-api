from fastapi import FastAPI
from .database import engine
from .models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def get_root():
    return {"message": "Fastapi server"}
