from src.api.v1.endpoints.services import (
    check_geolocation_exists_in_db,
    get_geolocation_from_db,
)
from src.models import IpGeolocation
from src.validators import IpGeolocationModel


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


def test_geolocation_exists_with_matching_ip_and_url(session):
    session.add(
        IpGeolocation(
            ip="192.168.1.1",
            url="example.com",
            continent_code="NA",
            continent_name="North America",
            country_code="US",
            country_name="United States",
            region_code="CA",
            region_name="California",
            city="Los Angeles",
            latitude=34.0522,
            longitude=-118.2437,
        )
    )
    session.commit()

    geolocation = IpGeolocationModel(
        ip="192.168.1.1",
        url="example.com",
        continent_code="NA",
        continent_name="North America",
        country_code="US",
        country_name="United States",
        region_code="CA",
        region_name="California",
        city="Los Angeles",
        latitude=34.0522,
        longitude=-118.2437,
    )

    result = check_geolocation_exists_in_db(geolocation, session)
    assert result is True


def test_geolocation_not_exists_with_different_ip_and_url(session):
    session.add(
        IpGeolocation(
            ip="192.168.1.2",
            url="other.com",
            continent_code="NA",
            continent_name="North America",
            country_code="US",
            country_name="United States",
            region_code="CA",
            region_name="California",
            city="Los Angeles",
            latitude=34.0522,
            longitude=-118.2437,
        )
    )
    session.commit()

    geolocation = IpGeolocationModel(
        ip="192.168.1.1",
        url="example.com",
        continent_code="NA",
        continent_name="North America",
        country_code="US",
        country_name="United States",
        region_code="CA",
        region_name="California",
        city="Los Angeles",
        latitude=34.0522,
        longitude=-118.2437,
    )

    result = check_geolocation_exists_in_db(geolocation, session)
    assert result is False


def test_geolocation_exists_with_null_ip_or_url(session):
    session.add(
        IpGeolocation(
            ip=None,
            url="example.com",
            continent_code="NA",
            continent_name="North America",
            country_code="US",
            country_name="United States",
            region_code="CA",
            region_name="California",
            city="Los Angeles",
            latitude=34.0522,
            longitude=-118.2437,
        )
    )
    session.commit()

    geolocation = IpGeolocationModel(
        ip=None,
        url="example.com",
        continent_code="NA",
        continent_name="North America",
        country_code="US",
        country_name="United States",
        region_code="CA",
        region_name="California",
        city="Los Angeles",
        latitude=34.0522,
        longitude=-118.2437,
    )

    result = check_geolocation_exists_in_db(geolocation, session)
    assert result is True


def test_geolocation_not_exists_with_null_ip_or_url(session):
    session.add(
        IpGeolocation(
            ip=None,
            url="example.com",
            continent_code="NA",
            continent_name="North America",
            country_code="US",
            country_name="United States",
            region_code="CA",
            region_name="California",
            city="Los Angeles",
            latitude=34.0522,
            longitude=-118.2437,
        )
    )
    session.commit()

    geolocation = IpGeolocationModel(
        ip=None,
        url="notfound.com",
        continent_code="NA",
        continent_name="North America",
        country_code="US",
        country_name="United States",
        region_code="CA",
        region_name="California",
        city="Los Angeles",
        latitude=34.0522,
        longitude=-118.2437,
    )

    result = check_geolocation_exists_in_db(geolocation, session)
    assert result is False
