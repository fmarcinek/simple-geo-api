import pytest
from pydantic import ValidationError

from src.validators import IpGeolocationModel, LanguageModel, LocationModel


def test_valid_latitude_and_longitude():
    geolocation = IpGeolocationModel(
        ip="162.158.103.87",
        continent_code="EU",
        continent_name="Europe",
        country_code="PL",
        country_name="Poland",
        region_code="MZ",
        region_name="Mazovia",
        city="Warsaw",
        latitude=52.2317,
        longitude=21.0183,
        type="ipv4",
        url=None,
    )
    assert geolocation.latitude == 52.2317
    assert geolocation.longitude == 21.0183


def test_invalid_latitude():
    with pytest.raises(ValidationError):
        IpGeolocationModel(
            ip="162.158.103.87",
            continent_code="EU",
            continent_name="Europe",
            country_code="PL",
            country_name="Poland",
            region_code="MZ",
            region_name="Mazovia",
            city="Warsaw",
            latitude=100.0,
            longitude=21.0183,
            type="ipv4",
            url=None,
        )


def test_invalid_longitude():
    with pytest.raises(ValidationError):
        IpGeolocationModel(
            ip="162.158.103.87",
            continent_code="EU",
            continent_name="Europe",
            country_code="PL",
            country_name="Poland",
            region_code="MZ",
            region_name="Mazovia",
            city="Warsaw",
            latitude=52.2317,
            longitude=200.0,
            type="ipv4",
            url=None,
        )


def test_invalid_ip_format():
    with pytest.raises(ValidationError):
        IpGeolocationModel(
            ip="999.999.999.999",
            continent_code="EU",
            continent_name="Europe",
            country_code="PL",
            country_name="Poland",
            region_code="MZ",
            region_name="Mazovia",
            city="Warsaw",
            latitude=52.2317,
            longitude=21.0183,
            type="ipv4",
            url=None,
        )


def test_missing_ip_and_url():
    with pytest.raises(ValidationError):
        IpGeolocationModel(
            ip=None,
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
            type="ipv4",
        )


def test_valid_ip_address():
    geolocation = IpGeolocationModel(
        ip="162.158.103.87",
        continent_code="EU",
        continent_name="Europe",
        country_code="PL",
        country_name="Poland",
        region_code="MZ",
        region_name="Mazovia",
        city="Warsaw",
        latitude=52.2317,
        longitude=21.0183,
        type="ipv4",
        url=None,
    )
    assert geolocation.ip == "162.158.103.87"


def test_language_model():
    language = LanguageModel(code="pl", name="Polish", native="Polski")
    assert language.code == "pl"
    assert language.name == "Polish"
    assert language.native == "Polski"


def test_location_model():
    language = LanguageModel(code="pl", name="Polish", native="Polski")
    location = LocationModel(
        geoname_id=756135,
        capital="Warsaw",
        country_flag="https://assets.ipstack.com/flags/pl.svg",
        country_flag_emoji="🇵🇱",
        country_flag_emoji_unicode="U+1F1F5 U+1F1F1",
        calling_code="48",
        is_eu=True,
        languages=[language],
    )
    assert location.capital == "Warsaw"
    assert location.country_flag == "https://assets.ipstack.com/flags/pl.svg"
    assert len(location.languages) == 1
    assert location.languages[0].code == "pl"


def test_non_empty_fields():
    with pytest.raises(ValidationError):
        IpGeolocationModel(
            ip="162.158.103.87",
            continent_code="EU",
            continent_name="Europe",
            country_code="PL",
            country_name="Poland",
            region_code="MZ",
            region_name="Mazovia",
            city="  ",
            latitude=52.2317,
            longitude=21.0183,
            type="ipv4",
            url=None,
        )
