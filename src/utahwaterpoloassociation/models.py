from pydantic import BaseModel
from typing import Optional, Tuple, ClassVar, Type, Any


def from_csv(cls, data):
    results = []
    for row in data:
        kwargs = {}
        for remote_key, local_key in cls.MAP.items():
            if remote_key.startswith("__"):
                kwargs[local_key] = None
            else:
                val = row[remote_key].strip()
                kwargs[local_key] = val

        results.append(cls(**kwargs))

    return results


class Organization(BaseModel):
    MAP: ClassVar[dict[str, str]] = {
        "Name": "name",
        "Full Name": "full_name",
    }
    name: str
    full_name: Optional[str]
    locations: list["Location"] = []

    @staticmethod
    def from_csv(data: list[dict]) -> list["Organization"]:
        return from_csv(Organization, data)


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


class Division(BaseModel):
    MAP: ClassVar[dict[str, str]] = {
        "Name": "name",
    }
    name: str

    @staticmethod
    def from_csv(data: list[dict]) -> list["Division"]:
        return from_csv(Division, data)

    def __hash__(self):
        return self.name.__hash__()


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
        return from_csv(Team, data)

    def key(self) -> Tuple[str, Division]:
        return (self.name, self.division)


class Game(BaseModel):
    MAP: ClassVar[dict[str, str]] = {
        "Date": "date",
        "Time": "time",
        "Location": "location_name",
        "Division": "division_name",
        "Away (White)": "away_team_name",
        "Away Score": "away_team_score",
        "Home (Dark)": "home_team_name",
        "Home Score": "home_team_score",
        "Winner": "winner_name",
        "Loser": "loser_name",
        "__division": "division",
        "__location": "location",
        "__away_team": "away_team",
        "__home_team": "home_team",
        "__winner": "winner",
        "__loser": "loser",
    }

    date: str
    time: str
    location_name: str
    division_name: str
    away_team_name: str
    away_team_score: Optional[str]
    home_team_name: str
    home_team_score: Optional[str]
    winner_name: Optional[str]
    loser_name: Optional[str]

    location: Optional[Location]
    division: Optional[Division]

    away_team: Optional[Team]
    home_team: Optional[Team]
    winner: Optional[Team]
    loser: Optional[Team]

    @staticmethod
    def from_csv(data: list[dict]) -> list["Game"]:
        return from_csv(Game, data)

    def valid(self):
        return all(
            [
                self.division != "",
                self.away_team_name != "",
                self.home_team_name != "",
            ]
        )

    def hydrate_from_league(self, l: "Leauge"):
        if not self.valid():
            return

        self.division = l.divisions[self.division_name]
        self.location = l.locations[self.location_name]

        self.home_team = l.teams[(self.home_team_name, self.division)]
        self.away_team = l.teams[(self.away_team_name, self.division)]

        if self.winner_name:
            self.winner = l.teams[(self.winner_name, self.division)]

        if self.loser_name:
            self.loser = l.teams[(self.loser_name, self.division)]


class SectionConfig(BaseModel):
    label: str
    gid: str
    model: Type[BaseModel]


SECTIONS: list[SectionConfig] = [
    SectionConfig(label="Organizations", gid="0", model=Organization),
    SectionConfig(label="Locations", gid="1642579731", model=Location),
    SectionConfig(label="Divisions", gid="99051020", model=Division),
    SectionConfig(label="Teams", gid="2085958623", model=Team),
    SectionConfig(label="Games", gid="424067115", model=Game),
]


class Leauge(BaseModel):
    organizations: dict[str, Organization] = {}
    locations: dict[str, Location] = {}
    divisions: dict[str, Division] = {}
    teams: dict[Tuple[str, Division], Team] = {}
    games: list[Game] = []

    def add_data(self, d: BaseModel):
        if isinstance(d, Organization):
            self.organizations[d.name] = d
        elif isinstance(d, Location):
            d.organization = self.organizations[d.organization_name]
            self.locations[d.organization_name] = d
        elif isinstance(d, Division):
            self.divisions[d.name] = d
        elif isinstance(d, Team):
            d.organization = self.organizations[d.organization_name]
            d.division = self.divisions[d.division_name]
            self.teams[(d.name, d.division)] = d
        elif isinstance(d, Game):
            d.hydrate_from_league(self)
            self.games.append(d)


class Data(BaseModel):
    league: Leauge
    meta: dict[str, Any]
