import os
from slugify import slugify
from pydantic import BaseModel
from typing import Optional, Tuple, ClassVar
from .csv import from_csv
from .organization import Organization
from .division import Division


class Team(BaseModel):
    MAP: ClassVar[dict[str, str]] = {
        "Team": "name",
        "Organization": "organization_name",
        "Leauge": "division_name",
        "__division": "division",
        "__organization": "organization",
    }

    name: str
    organization_name: str
    division_name: str
    division: Optional[Division]
    organization: Optional[Organization]

    @staticmethod
    def from_csv(data: list[dict]) -> list["Team"]:
        data = [x for x in data if x.get("name")]
        return from_csv(Team, data)

    def key(self) -> Tuple[str, Division]:
        return "-".join([self.name, self.division.name])

    def slug(self) -> str:
        return slugify(self.name.replace("'", ""))

    def url(self):
        os.path.join(self.organization.slug(), self.division.slug(), self.slug())
