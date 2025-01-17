from unittest.mock import patch

import pytest

from src.models import IpGeolocation, Language, Location


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
