import ipaddress
from typing import Tuple

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.validators import IpGeolocationModel, normalize_url

from .ipstack_api import fetch_geolocation_from_external_source
from .services import get_geolocation_from_db

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def validate_and_normalize_ip_or_url(ip_or_url_value: str) -> Tuple[str, str]:
    try:
        normalized_value = ipaddress.ip_address(ip_or_url_value)
        return str(normalized_value), "ip"
    except ValueError:
        normalized_value = normalize_url(ip_or_url_value)
        if not normalized_value:
            raise HTTPException(
                status_code=400, detail="GET parameter must be Ipv4, Ipv6 or URL value"
            )
        return normalized_value, "url"


@router.get("/{ip_or_url_value}", response_model=IpGeolocationModel)
def get_geolocation(ip_or_url_value: str, db: Session = Depends(get_db)):
    normalized_value, value_type = validate_and_normalize_ip_or_url(ip_or_url_value)

    try:
        geolocation = get_geolocation_from_db(
            ip_or_url_value=normalized_value, value_type=value_type, db=db
        )
        if geolocation:
            return IpGeolocationModel(**geolocation.as_dict())

        geolocation_model = fetch_geolocation_from_external_source(normalized_value)
        if geolocation_model:
            return geolocation_model

        raise HTTPException(status_code=404, detail="Geolocation not found")

    except RuntimeError:
        geolocation_model = fetch_geolocation_from_external_source(normalized_value)
        if geolocation_model:
            return geolocation_model
        raise HTTPException(status_code=500, detail="Database connection error")
