import ipaddress
from typing import Tuple

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.models import IpGeolocation, Language, Location
from src.validators import IpGeolocationModel, normalize_url

from .ipstack_api import fetch_geolocation_from_external_source
from .services import check_geolocation_exists_in_db, get_geolocation_from_db

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
                status_code=400, detail="Parameter must be Ipv4, Ipv6 or URL value"
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


@router.post("", response_model=IpGeolocationModel, status_code=201)
def create_geolocation(geolocation: IpGeolocationModel, db: Session = Depends(get_db)):
    entry_exists = check_geolocation_exists_in_db(geolocation, db)
    if entry_exists:
        raise HTTPException(
            status_code=400,
            detail="An entry with the same IP or URL already exists.",
        )
    try:
        # create or find Location and its related Languages
        location_data = geolocation.location
        if location_data:
            languages = []
            for lang_data in location_data.languages:
                language = db.query(Language).filter_by(code=lang_data.code).first()
                if not language:
                    language = Language(**lang_data.model_dump())
                    db.add(language)
                languages.append(language)

            location = (
                db.query(Location)
                .filter_by(geoname_id=location_data.geoname_id)
                .first()
            )
            if not location:
                location = Location(
                    **{
                        key: value
                        for key, value in location_data.model_dump().items()
                        if key != "languages"
                    }
                )
                location.languages = languages
                db.add(location)
        else:
            location = None

        # create IpGeolocation record
        new_ip_geolocation = IpGeolocation(
            **{
                key: value
                for key, value in geolocation.model_dump().items()
                if key != "location"
            }
        )
        new_ip_geolocation.location = location

        db.add(new_ip_geolocation)
        db.commit()
        db.refresh(new_ip_geolocation)

        return new_ip_geolocation.as_dict()

    except Exception as e:
        print(f"Error creating geolocation: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating geolocation")


@router.delete("/{ip_or_url_value}", status_code=204)
def delete_geolocation(ip_or_url_value: str, db: Session = Depends(get_db)):
    normalized_value, value_type = validate_and_normalize_ip_or_url(ip_or_url_value)

    try:
        geolocation = get_geolocation_from_db(
            ip_or_url_value=normalized_value, value_type=value_type, db=db
        )
        if not geolocation:
            raise HTTPException(status_code=404, detail="Geolocation not found")
    except RuntimeError:
        raise HTTPException(status_code=500, detail="Database connection error")

    db.delete(geolocation)
    db.commit()

    return {"detail": "Geolocation deleted successfully"}
