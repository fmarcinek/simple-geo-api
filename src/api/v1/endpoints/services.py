from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.models import IpGeolocation


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
        raise RuntimeError("Database query failed") from e
