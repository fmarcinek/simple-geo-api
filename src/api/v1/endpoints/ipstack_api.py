import os
from typing import Optional

import requests

from src.models import IpGeolocation
from src.validators import IpGeolocationModel


class NoIpStackAccessKeyException(Exception):
    pass


IP_STACK_API_URL = "http://api.ipstack.com/{search_value}"


def fetch_geolocation_from_external_source(
    normalized_value: str,
) -> Optional[IpGeolocation]:
    """
    Fetches geolocation data from an external API (ipstack.com)
    and converts it into IpGeolocation.
    """
    ip_stack_access_key = os.getenv("IP_STACK_API_ACCESS_KEY")

    try:
        if not ip_stack_access_key:
            raise NoIpStackAccessKeyException()
        response = requests.get(
            IP_STACK_API_URL.format(search_value=normalized_value),
            timeout=5,
            params={"access_key": ip_stack_access_key, "output": "json"},
        )
        response.raise_for_status()

        data = response.json()
        geolocation = IpGeolocationModel(**data)

        return geolocation
    except Exception as e:
        print(f"Error fetching geolocation data from ip stack: {e}")
        return None
