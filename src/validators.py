import ipaddress
from typing import List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, model_validator


def normalize_url(url: str) -> str:
    try:
        if not urlparse(url).scheme:
            url = f"http://{url}"

        parsed_url = urlparse(url)
        if parsed_url.netloc and "." in parsed_url.netloc:
            return parsed_url.netloc
        return ""
    except ValueError:
        return ""


class LanguageModel(BaseModel):
    id: Optional[int] = None
    code: str = Field(..., min_length=1, max_length=5)
    name: str
    native: str

    @field_validator("code", "name", "native")
    def non_empty_fields(cls, value):
        if not value.strip():
            raise ValueError(f"{value} cannot be empty or whitespace")
        return value


class LocationModel(BaseModel):
    id: Optional[int] = None
    geoname_id: int
    capital: str
    country_flag: str
    country_flag_emoji: str
    country_flag_emoji_unicode: str
    calling_code: str
    is_eu: bool
    languages: Optional[List[LanguageModel]] = []

    @field_validator(
        "capital",
        "country_flag",
        "country_flag_emoji",
        "country_flag_emoji_unicode",
        "calling_code",
    )
    def non_empty_fields(cls, value):
        if not value.strip():
            raise ValueError(f"{value} cannot be empty or whitespace")
        return value


class IpGeolocationModel(BaseModel):
    id: Optional[int] = None
    ip: Optional[str] = None
    type: Optional[str] = Field(None, pattern=r"^(ipv4|ipv6)$")
    url: Optional[str] = None
    continent_code: str
    continent_name: str
    country_code: str
    country_name: str
    region_code: str
    region_name: str
    city: str
    zip: Optional[str] = None
    latitude: float
    longitude: float
    msa: Optional[str] = None
    dma: Optional[str] = None
    radius: Optional[str] = None
    ip_routing_type: Optional[str] = None
    connection_type: Optional[str] = None
    location: Optional[LocationModel] = None

    @field_validator(
        "continent_code",
        "continent_name",
        "country_code",
        "country_name",
        "region_code",
        "region_name",
        "city",
    )
    def non_empty_fields(cls, value):
        if not value.strip():
            raise ValueError(f"{value} cannot be empty or whitespace")
        return value

    @model_validator(mode="before")
    def check_ip_or_url_required(cls, values):
        ip = values.get("ip")
        url = values.get("url")

        if ip is None and url is None:
            raise ValueError("At least one of 'ip' or 'url' must not be null")
        return values

    @field_validator("ip")
    def check_ip_address_and_normalize(cls, ip_address):
        try:
            normalized_ip_address = ipaddress.ip_address(ip_address)
            return str(normalized_ip_address)
        except ValueError:
            raise ValueError("'ip' field must be either ipv4 or ipv6 standard")

    @field_validator("url")
    def check_url_and_normalize(cls, url):
        if url and not normalize_url(url):
            raise ValueError("'url' field must be a correct url address")
        return normalize_url(url)

    @field_validator("latitude")
    def validate_latitude(cls, v):
        if not (-90 <= v <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    def validate_longitude(cls, v):
        if not (-180 <= v <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v
