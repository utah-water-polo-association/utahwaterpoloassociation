from pydantic import BaseModel
from .organization import Organization
from .location import Location
from .team import Team
from .contact import Contact


class DirectoryEntry(BaseModel):
    organization: Organization
    teams: dict[str, Team] = {}
    locations: list[Location] = []
    contacts: list[Contact] = []
    teams_by_division: dict[str, list[Team]] = {}
