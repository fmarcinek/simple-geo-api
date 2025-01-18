import pytest

from src.models import IpGeolocation


@pytest.fixture
def sample_geolocation(session):
    geolocation = IpGeolocation(
        ip="162.158.103.87",
        type="ipv4",
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
    session.refresh(geolocation)
    return geolocation


def test_delete_geolocation_success(client, session, sample_geolocation):
    ip_or_url_value = sample_geolocation.ip

    response = client.delete(f"/geolocations/{ip_or_url_value}")
    assert response.status_code == 204
    assert (
        session.query(IpGeolocation).filter(IpGeolocation.ip == ip_or_url_value).first()
        is None
    )


def test_delete_geolocation_database_error(client, mock_db_session):
    mock_db_session.side_effect = RuntimeError("Database connection error")

    response = client.delete("/geolocations/162.158.103.87")
    assert response.status_code == 500
    assert response.json() == {"detail": "Database connection error"}


def test_delete_geolocation_not_found(client):
    response = client.delete("/geolocations/nonexistent.value")
    assert response.status_code == 404
    assert response.json() == {"detail": "Geolocation not found"}


def test_delete_geolocation_bad_request(client):
    response = client.delete("/geolocations/malformed_value")
    assert response.status_code == 400
    assert response.json() == {"detail": "Parameter must be Ipv4, Ipv6 or URL value"}
