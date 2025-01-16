import pytest

from src.models import IpGeolocation, Language, Location


@pytest.mark.parametrize(
    "languages",
    [
        [],
        [Language(code="pl", name="Polish", native="Polski")],
        [
            Language(code="en", name="English", native="English"),
            Language(code="fr", name="French", native="Français"),
        ],
    ],
)
def test_create_and_store_ip_geolocation_full(session, languages):
    location = Location(
        geoname_id=756135,
        capital="Warsaw",
        country_flag="https://assets.ipstack.com/flags/pl.svg",
        country_flag_emoji="🇵🇱",
        country_flag_emoji_unicode="U+1F1F5 U+1F1F1",
        calling_code="48",
        is_eu=True,
        languages=languages,
    )

    new_ip_geolocation = IpGeolocation(
        ip="162.158.103.87",
        type="ipv4",
        continent_code="EU",
        continent_name="Europe",
        country_code="PL",
        country_name="Poland",
        region_code="MZ",
        region_name="Mazovia",
        city="Warsaw",
        zip="00-025",
        latitude=52.2317008972168,
        longitude=21.0183391571045,
        ip_routing_type="fixed",
        connection_type="tx",
        location=location,
    )

    session.add(new_ip_geolocation)
    session.commit()

    ip_geolocation = session.query(IpGeolocation).first()

    assert new_ip_geolocation == ip_geolocation
