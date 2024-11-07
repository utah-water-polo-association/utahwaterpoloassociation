from pydantic import BaseModel
from typing import Optional, ClassVar
from .csv import from_csv
from .organization import Organization


class Location(BaseModel):
    MAP: ClassVar[dict[str, str]] = {
        "Short Name": "organization_name",
        "Long Name": "name",
        "Address": "address",
        "__organization": "organization",
    }
    organization_name: str
    name: str
    address: str
    organization: Optional[Organization]

    @staticmethod
    def from_csv(data: list[dict]) -> list["Location"]:
        return from_csv(Location, data)
