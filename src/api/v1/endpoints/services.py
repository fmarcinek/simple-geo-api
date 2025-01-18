from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.models import IpGeolocation
from src.validators import IpGeolocationModel


def get_geolocation_from_db(
    ip_or_url_value: str, value_type: str, db: Session
) -> IpGeolocation | None:
    try:
        if value_type == "ip":
            return (
                db.query(IpGeolocation)
                .filter((IpGeolocation.ip == ip_or_url_value))
                .first()
            )
        else:
            return (
                db.query(IpGeolocation)
                .filter((IpGeolocation.url == ip_or_url_value))
                .first()
            )
    except (SQLAlchemyError, DBAPIError) as e:
        print(f"Database query failed: {e}")
        raise RuntimeError("Database query failed") from e


def check_geolocation_exists_in_db(
    geolocation: IpGeolocationModel, db: Session
) -> bool:
    conditions = []
    if geolocation.ip:
        conditions.append(IpGeolocation.ip == geolocation.ip)
    if geolocation.url:
        conditions.append(IpGeolocation.url == geolocation.url)

    existing_entry = db.query(IpGeolocation).filter(*conditions).first()

    return existing_entry is not None
