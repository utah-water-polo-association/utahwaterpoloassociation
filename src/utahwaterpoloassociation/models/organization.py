from slugify import slugify
from pydantic import BaseModel
from typing import Optional, ClassVar
from .csv import from_csv


class Organization(BaseModel):
    MAP: ClassVar[dict[str, str]] = {
        "Name": "name",
        "Full Name": "full_name",
    }
    name: str
    full_name: Optional[str]

    @staticmethod
    def from_csv(data: list[dict]) -> list["Organization"]:
        return from_csv(Organization, data)

    def to_serializable(self) -> dict:
        """Converts the model to a dictionary format that can be serialized."""

        return self.model_dump(mode="json", exclude=["locations"])

    def slug(self) -> str:
        return slugify(self.name.replace("'", ""))
