import ipaddress

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.validators import IpGeolocationModel, normalize_url

from .services import get_geolocation_from_db

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{ip_or_url_value}", response_model=IpGeolocationModel)
def get_geolocation(ip_or_url_value: str, db: Session = Depends(get_db)):
    try:
        normalized_value = ipaddress.ip_address(ip_or_url_value)
        normalized_value = str(normalized_value)
        ip_type = "ip"
    except ValueError:
        normalized_value = normalize_url(ip_or_url_value)
        ip_type = "url"
        if not normalized_value:
            raise HTTPException(
                status_code=400, detail="GET parameter must be Ipv4, Ipv6 or URL value"
            )
    try:
        geolocation = get_geolocation_from_db(
            ip_or_url_value=normalized_value, value_type=ip_type, db=db
        )

        if geolocation is None:
            raise HTTPException(status_code=404, detail="Geolocation not found")
        return IpGeolocationModel(**geolocation.as_dict())

    except RuntimeError:
        raise HTTPException(status_code=500, detail="Database connection error")
