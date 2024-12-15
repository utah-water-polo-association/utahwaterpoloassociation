from pydantic import BaseModel
from datetime import datetime, timedelta
from .organization import Organization
from .location import Location
from .division import Division
from .team import Team
from .game import Game
from .contact import Contact
from .directory_entry import DirectoryEntry

from .hashable import Hashable

ALL_DIVISION = "All"
DIVISION_ORDER = [
    "HS Varsity Boys",
    "18u Boys",
    "HS Varsity Girls",
    "18u Girls",
    "HS Combined Boys",
    "16u Boys",
    "HS Combined Girls",
    "16u Girls",
    "HS JV Boys",
    "14u Boys",
    "14u Girls",
    "10u Mixed",
    "12u Mixed",
]


DIVISION_AND_ALL = [ALL_DIVISION] + DIVISION_ORDER


class Schedule(BaseModel):
    # by_team: dict[str, list[Game]]
    by_division: dict[str, list[Game]]
    games: list[Game]

    @property
    def division_order(self) -> list[str]:
        return [x for x in DIVISION_AND_ALL if x in self.by_division]

    def add_game(self, game: Game):
        # if game.away_team_name not in self.by_team:
        #     self.by_team[game.away_team_name] = []

        # if game.home_team_name not in self.by_team:
        #     self.by_team[game.home_team_name] = []

        if game.division_name not in self.by_division:
            self.by_division[game.division_name] = []

        if ALL_DIVISION not in self.by_division:
            self.by_division[ALL_DIVISION] = []

        self.by_division[ALL_DIVISION].append(game)
        # self.by_team[game.away_team_name].append(game)
        # self.by_team[game.home_team_name].append(game)
        self.by_division[game.division_name].append(game)
        self.games.append(game)


class Leauge(Hashable):
    organizations: dict[str, Organization] = {}
    locations: dict[str, Location] = {}
    divisions: dict[str, Division] = {}
    teams: dict[str, Team] = {}
    games: list[Game] = []
    contacts: list[Contact] = []

    def unreported_games(self, division):
        nw = datetime.now() + timedelta(days=1)
        games = filter(lambda x: x.parsed_date() <= nw, self.games)
        games = filter(lambda x: not x.reported(), games)
        games = list(filter(lambda x: x.division_name == division, games))
        return games

    def schedule(self) -> Schedule:
        schedule = Schedule(
            by_team={}, by_division={}, games=[], division_order=DIVISION_AND_ALL
        )
        for game in self.games:
            schedule.add_game(game)

        return schedule

    def directory(self) -> list[DirectoryEntry]:
        directory_items: list[DirectoryEntry] = []
        teams_by_division: dict[str, list[Team]] = {}

        for _, o in self.organizations.items():
            d = DirectoryEntry(organization=o)
            d.locations = [
                l
                for (_, l) in self.locations.items()
                if l.organization == d.organization
            ]

            d.teams = {}
            for key, t in self.teams.items():
                if not teams_by_division.get(t.division.slug()):
                    teams_by_division[t.division.slug()] = []
                teams_by_division[t.division.slug()].append(t)
                if t.organization != d.organization:
                    continue

                d.teams[key] = t

            d.contacts = [c for c in self.contacts if c.organization == d.organization]

            directory_items.append(d)

        return directory_items

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
            self.teams[d.key()] = d
        elif isinstance(d, Game):
            d.hydrate_from_league(self)
            if d.valid():
                self.games.append(d)
        elif isinstance(d, Contact):
            d.organization = self.organizations[d.organization_name]
            self.contacts.append(d)
