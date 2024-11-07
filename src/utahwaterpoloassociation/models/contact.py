from pydantic import BaseModel
from typing import Optional, ClassVar
from .csv import from_csv
from .organization import Organization


class Contact(BaseModel):
    MAP: ClassVar[dict[str, str]] = {
        "Team Name": "organization_name",
        "Role": "role",
        "Name": "name",
        "Phone Number": "phone_number",
        "Email": "email",
        "Notes": "notes",
        "__organization": "organization",
    }
    organization_name: str
    role: str
    name: str
    phone_number: str
    email: str
    notes: str
    organization: Optional[Organization]

    @staticmethod
    def from_csv(data: list[dict]) -> list["Contact"]:
        return from_csv(Contact, data)
