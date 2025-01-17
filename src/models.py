from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

location_language_association = Table(
    "location_language_association",
    Base.metadata,
    Column("location_id", Integer, ForeignKey("locations.id"), primary_key=True),
    Column("language_id", Integer, ForeignKey("languages.id"), primary_key=True),
)


class Language(Base):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    native = Column(String, nullable=False)

    def as_dict(self):
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column.name != "id"
        }


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    geoname_id = Column(Integer, nullable=False)
    capital = Column(String, nullable=False)
    country_flag = Column(String, nullable=False)
    country_flag_emoji = Column(String, nullable=False)
    country_flag_emoji_unicode = Column(String, nullable=False)
    calling_code = Column(String, nullable=False)
    is_eu = Column(Boolean, nullable=False)

    # relationship many-to-many using auxiliary 'location_language_association' table
    languages = relationship("Language", secondary=location_language_association)

    def as_dict(self):
        columns = self.__table__.columns
        result = {column.name: getattr(self, column.name) for column in columns}
        del result["id"]

        if self.languages:
            result["languages"] = [language.as_dict() for language in self.languages]

        return result


class IpGeolocation(Base):
    __tablename__ = "ip_geolocations"

    id = Column(Integer, primary_key=True)
    ip = Column(String, index=True)
    type = Column(String)
    url = Column(String, index=True)
    continent_code = Column(String, nullable=False)
    continent_name = Column(String, nullable=False)
    country_code = Column(String, nullable=False)
    country_name = Column(String, nullable=False)
    region_code = Column(String, nullable=False)
    region_name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    zip = Column(String)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    msa = Column(String)
    dma = Column(String)
    radius = Column(String)
    ip_routing_type = Column(String)
    connection_type = Column(String)

    location_id = Column(Integer, ForeignKey("locations.id"))
    location = relationship("Location", backref="ip_geolocations", uselist=False)

    __table_args__ = (
        CheckConstraint(
            "(ip IS NOT NULL OR url IS NOT NULL)", name="ip_or_url_not_null"
        ),
    )

    def as_dict(self):
        columns = self.__table__.columns
        result = {column.name: getattr(self, column.name) for column in columns}
        del result["id"]

        if self.location:
            result["location"] = self.location.as_dict()

        return result
