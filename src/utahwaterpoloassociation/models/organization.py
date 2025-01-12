from slugify import slugify
from pydantic import BaseModel, Field
from typing import Optional, ClassVar
from .csv import from_csv


class Organization(BaseModel):
    MAP: ClassVar[dict[str, str]] = {
        "Name": "name",
        "Full Name": "full_name",
        "Pool Name": "pool_name",
        "Address": "address",
        "Website": "website",
        "Logo Link": "logo_link",
        "Date Of Last Update": "date_of_last_update",
        "Latitude": "latitude",
        "Longitude": "longitude",
    }
    name: str
    full_name: Optional[str] = Field(default=None, required=False)
    pool_name: Optional[str] = Field(default=None, required=False)
    address: Optional[str] = Field(default=None, required=False)
    website: Optional[str] = Field(default=None, required=False)
    logo_link: Optional[str] = Field(
        default="/icons/waterpolo.webp",
        required=False,
    )
    date_of_last_update: Optional[str] = Field(default=None, required=False)
    latitude: Optional[str] = Field(default=None, required=False)
    longitude: Optional[str] = Field(default=None, required=False)

    @staticmethod
    def from_csv(data: list[dict]) -> list["Organization"]:
        return from_csv(Organization, data)

    def to_serializable(self) -> dict:
        """Converts the model to a dictionary format that can be serialized."""

        return self.model_dump(mode="json", exclude=["locations"])

    def icon_path(self) -> str:
        return f"/icons/{self.slug()}.webp"

    def slug(self) -> str:
        return slugify(self.name.replace("'", ""))
