import pytest

from src.models import IpGeolocation, Language, Location


@pytest.fixture
def sample_ip_geolocation():
    return {
        "ip": "192.168.1.1",
        "type": "ipv4",
        "continent_code": "NA",
        "continent_name": "North America",
        "country_code": "US",
        "country_name": "United States",
        "region_code": "CA",
        "region_name": "California",
        "city": "Mountain View",
        "latitude": 37.386,
        "longitude": -122.0838,
        "location": {
            "geoname_id": 123456,
            "capital": "Washington D.C.",
            "country_flag": "https://example.com/flag.png",
            "country_flag_emoji": "🇺🇸",
            "country_flag_emoji_unicode": "U+1F1FA U+1F1F8",
            "calling_code": "1",
            "is_eu": False,
            "languages": [{"code": "en", "name": "English", "native": "English"}],
        },
    }


def test_post_ip_geolocation_success(client, session, sample_ip_geolocation):
    response = client.post("/geolocations", json=sample_ip_geolocation)
    assert response.status_code == 201
    data = response.json()

    assert data["ip"] == "192.168.1.1"
    assert data["continent_name"] == "North America"
    assert data["location"]["geoname_id"] == 123456
    assert len(data["location"]["languages"]) == 1
    assert data["location"]["languages"][0]["code"] == "en"


def test_post_ip_geolocation_duplicate_ip(client, session, sample_ip_geolocation):
    languages_data = sample_ip_geolocation["location"].pop("languages")
    languages = [Language(**lang) for lang in languages_data]
    location_data = sample_ip_geolocation.pop("location")
    location = Location(**location_data, languages=languages)

    ip_geolocation = IpGeolocation(**sample_ip_geolocation, location=location)
    session.add(ip_geolocation)
    session.commit()

    response = client.post("/geolocations", json=sample_ip_geolocation)
    assert response.status_code == 400


def test_post_ip_geolocation_invalid_data(client, session):
    invalid_data = {
        "ip": "192.168.1.1",
        "type": "ipv4",
        "continent_code": "",
        "continent_name": "",
        "country_code": "",
        "country_name": "",
        "region_code": "",
        "region_name": "",
        "city": "",
        "latitude": "invalid_latitude",  # invalid format
        "longitude": -122.0838,
    }

    response = client.post("/geolocations", json=invalid_data)
    assert response.status_code == 422


def test_post_ip_geolocation_missing_location(client, session, sample_ip_geolocation):
    del sample_ip_geolocation["location"]

    response = client.post("/geolocations", json=sample_ip_geolocation)
    assert response.status_code == 201
    data = response.json()

    assert data["ip"] == "192.168.1.1"
    assert data["location"] is None
