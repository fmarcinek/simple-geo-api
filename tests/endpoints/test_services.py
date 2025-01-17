from src.api.v1.endpoints.services import get_geolocation_from_db
from src.models import IpGeolocation


def test_get_geolocation_from_db_ip(session):
    geolocation = IpGeolocation(
        ip="162.158.103.87",
        type="ipv4",
        url=None,
        continent_code="EU",
        continent_name="Europe",
        country_code="PL",
        country_name="Poland",
        region_code="MZ",
        region_name="Mazovia",
        city="Warsaw",
        latitude=52.2317,
        longitude=21.0183,
    )
    session.add(geolocation)
    session.commit()

    result = get_geolocation_from_db("162.158.103.87", "ip", session)
    assert result is not None
    assert result.ip == "162.158.103.87"
    assert result.country_name == "Poland"


def test_get_geolocation_from_db_url(session):
    geolocation = IpGeolocation(
        ip=None,
        type="url",
        url="example.com",
        continent_code="EU",
        continent_name="Europe",
        country_code="PL",
        country_name="Poland",
        region_code="MZ",
        region_name="Mazovia",
        city="Warsaw",
        latitude=52.2317,
        longitude=21.0183,
    )
    session.add(geolocation)
    session.commit()

    result = get_geolocation_from_db("example.com", "url", session)
    assert result is not None
    assert result.url == "example.com"
    assert result.country_name == "Poland"


def test_get_geolocation_from_db_not_found(session):
    result = get_geolocation_from_db("nonexistent.com", "url", session)
    assert result is None
