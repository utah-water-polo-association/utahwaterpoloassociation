import os
from slugify import slugify
from pydantic import BaseModel
from typing import Optional, Tuple, ClassVar
from .csv import from_csv
from .organization import Organization
from .division import Division

NAMES_TO_ICON = {
    "Bear River": "bearriver",
    "Brighton": "brighton",
    "Cache": "waterpolo",
    "Canyon View": "waterpolo",
    "Cedar": "cedar",
    "Cyprus": "cyprus",
    "Kearns": "kearns",
    "Murray": "murray",
    "Ogden": "ogden",
    "Olympus": "olympus",
    "Park City": "parkcity",
    "SUWP": "waterpolo",
    "Skyline": "skyline",
    "South Davis": "southdavis",
    "Tooele": "waterpolo",
    "UCO": "waterpolo",
    "United": "waterpolo",
    "Wasatch": "wasatch",
}


class Team(BaseModel):
    MAP: ClassVar[dict[str, str]] = {
        "Team Name": "name",
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
        data = [x for x in data if x.get("Team Name")]
        return from_csv(Team, data)

    def key(self) -> Tuple[str, Division]:
        return "-".join([self.name, self.division.name])

    def slug(self) -> str:
        return slugify(self.name.replace("'", ""))

    def url(self):
        os.path.join(self.organization.slug(), self.division.slug(), self.slug())

    def icon(self) -> str:
        name = NAMES_TO_ICON.get(self.organization_name, "waterpolo")

        return "/icons/%s.png" % (name)
