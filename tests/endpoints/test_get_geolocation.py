from unittest.mock import patch

import pytest

from src.models import IpGeolocation, Language, Location
from src.validators import IpGeolocationModel


@pytest.fixture
def mock_db_session():
    with patch("src.api.v1.endpoints.geolocations.get_geolocation_from_db") as mock_db:
        yield mock_db


def test_valid_ipv4(mock_db_session, client):
    mock_db_session.return_value = IpGeolocation(
        **{
            "id": 123,
            "ip": "160.158.103.87",
            "type": "ipv4",
            "continent_code": "EU",
            "continent_name": "Europe",
            "country_code": "PL",
            "country_name": "Poland",
            "region_code": "MZ",
            "region_name": "Mazovia",
            "city": "Warsaw",
            "latitude": 52.2317,
            "longitude": 21.0183,
        }
    )

    response = client.get("/geolocations/160.158.103.87")
    assert response.status_code == 200
    assert response.json()["ip"] == "160.158.103.87"
    assert response.json()["type"] == "ipv4"


def test_valid_url(mock_db_session, client):
    mock_db_session.return_value = IpGeolocation(
        **{
            "id": 123,
            "url": "example.com",
            "continent_code": "EU",
            "continent_name": "Europe",
            "country_code": "PL",
            "country_name": "Poland",
            "region_code": "MZ",
            "region_name": "Mazovia",
            "city": "Warsaw",
            "latitude": 52.2317,
            "longitude": 21.0183,
        }
    )

    response = client.get("/geolocations/example.com")
    assert response.status_code == 200
    assert response.json()["url"] == "example.com"
    assert response.json()["latitude"] == 52.2317


def test_invalid_ip_or_url(client):
    response = client.get("/geolocations/invalid_input")
    assert response.status_code == 400
    assert response.json()["detail"] == "GET parameter must be Ipv4, Ipv6 or URL value"


def test_geolocation_not_found(mock_db_session, client):
    mock_db_session.return_value = None

    response = client.get("/geolocations/160.158.103.87")
    assert response.status_code == 404
    assert response.json()["detail"] == "Geolocation not found"


def test_database_connection_error(mock_db_session, client):
    mock_db_session.side_effect = RuntimeError("Database connection error")

    response = client.get("/geolocations/160.158.103.87")
    assert response.status_code == 500
    assert response.json()["detail"] == "Database connection error"


def test_get_geolocation_success(session, client):
    lang_pl = Language(code="pl", name="Polish", native="Polski")
    location = Location(
        geoname_id=756135,
        capital="Warsaw",
        country_flag="https://assets.ipstack.com/flags/pl.svg",
        country_flag_emoji="🇵🇱",
        country_flag_emoji_unicode="U+1F1F5 U+1F1F1",
        calling_code="48",
        is_eu=True,
        languages=[lang_pl],
    )
    session.add(lang_pl, location)
    session.add(
        IpGeolocation(
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
            location=location,
        )
    )
    session.commit()

    response = client.get("/geolocations/162.158.103.87")
    assert response.status_code == 200
    assert response.json()["ip"] == "162.158.103.87"
    assert response.json()["country_name"] == "Poland"


def test_get_geolocation_with_external_source(session, client):
    session.add(
        IpGeolocation(
            ip="192.168.1.1",
            type="ipv4",
            url=None,
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

    mock_data = {
        "ip": "8.8.8.8",
        "type": "ipv4",
        "continent_code": "NA",
        "continent_name": "North America",
        "country_code": "US",
        "country_name": "United States",
        "region_code": "CA",
        "region_name": "California",
        "city": "Mountain View",
        "latitude": 37.3861,
        "longitude": -122.0839,
    }

    with patch(
        "src.api.v1.endpoints.geolocations.fetch_geolocation_from_external_source",
        return_value=IpGeolocationModel(**mock_data),
    ):
        # geolocation data are in database
        response = client.get("/geolocations/192.168.1.1")
        assert response.status_code == 200
        assert response.json()["ip"] == "192.168.1.1"
        assert response.json()["country_name"] == "United States"

        # no geolocation data in database, but it is in external source
        response = client.get("/geolocations/8.8.8.8")
        assert response.status_code == 200
        assert response.json()["ip"] == "8.8.8.8"
        assert response.json()["city"] == "Mountain View"

    # no geolocation data neither in database nor in external source
    with patch(
        "src.api.v1.endpoints.geolocations.fetch_geolocation_from_external_source",
        return_value=None,
    ):
        response = client.get("/geolocations/10.0.0.1")
        assert response.status_code == 404
        assert response.json()["detail"] == "Geolocation not found"
