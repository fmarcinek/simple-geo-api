import pytest
import requests
import responses

from src.api.v1.endpoints.ipstack_api import (
    IP_STACK_API_URL,
    fetch_geolocation_from_external_source,
)
from src.validators import IpGeolocationModel


@pytest.fixture
def set_ip_stack_key(monkeypatch):
    monkeypatch.setenv("IP_STACK_API_ACCESS_KEY", "test_key")


@pytest.fixture
def clear_ip_stack_key(monkeypatch):
    monkeypatch.delenv("IP_STACK_API_ACCESS_KEY", raising=False)


@responses.activate
def test_fetch_geolocation_success(set_ip_stack_key):
    normalized_value = "8.8.8.8"
    api_url = IP_STACK_API_URL.format(search_value=normalized_value)

    mock_response = {
        "ip": "8.8.8.8",
        "type": "ipv4",
        "continent_code": "NA",
        "continent_name": "North America",
        "country_code": "US",
        "country_name": "United States",
        "region_code": "CA",
        "region_name": "California",
        "city": "Mountain View",
        "latitude": 37.386,
        "longitude": -122.084,
    }

    responses.add(
        responses.GET,
        api_url,
        json=mock_response,
        status=200,
    )

    geolocation = fetch_geolocation_from_external_source(normalized_value)

    assert geolocation is not None
    assert isinstance(geolocation, IpGeolocationModel)
    assert geolocation.ip == "8.8.8.8"
    assert geolocation.country_name == "United States"


def test_fetch_geolocation_missing_access_key(clear_ip_stack_key):
    normalized_value = "8.8.8.8"

    geolocation = fetch_geolocation_from_external_source(normalized_value)
    assert geolocation is None


@responses.activate
def test_fetch_geolocation_api_error(set_ip_stack_key):
    normalized_value = "8.8.8.8"
    api_url = IP_STACK_API_URL.format(search_value=normalized_value)

    responses.add(
        responses.GET,
        api_url,
        status=500,
    )

    geolocation = fetch_geolocation_from_external_source(normalized_value)

    assert geolocation is None


@responses.activate
def test_fetch_geolocation_invalid_data(set_ip_stack_key):
    normalized_value = "8.8.8.8"
    api_url = IP_STACK_API_URL.format(search_value=normalized_value)

    mock_response = {
        "ip": "8.8.8.8",
        "type": "ipv4",
    }

    responses.add(
        responses.GET,
        api_url,
        json=mock_response,
        status=200,
    )

    geolocation = fetch_geolocation_from_external_source(normalized_value)

    assert geolocation is None


@responses.activate
def test_fetch_geolocation_timeout(set_ip_stack_key):
    normalized_value = "8.8.8.8"
    api_url = IP_STACK_API_URL.format(search_value=normalized_value)

    responses.add(
        responses.GET,
        api_url,
        body=requests.exceptions.Timeout(),
    )

    geolocation = fetch_geolocation_from_external_source(normalized_value)

    assert geolocation is None
