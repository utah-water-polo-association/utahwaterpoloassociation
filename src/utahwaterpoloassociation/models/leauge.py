from pydantic import BaseModel
from datetime import datetime, timedelta
from .organization import Organization
from .location import Location
from .division import Division
from .team import Team
from .game import Game
from .contact import Contact
from .tournament import Tournament
from .directory_entry import DirectoryEntry
from .schedule import Schedule, DIVISION_AND_ALL
from .hashable import Hashable


class Leauge(Hashable):
    organizations: dict[str, Organization] = {}
    locations: dict[str, Location] = {}
    divisions: dict[str, Division] = {}
    teams: dict[str, Team] = {}
    games: list[Game] = []
    contacts: list[Contact] = []
    tournaments: dict[str, Tournament] = {}

    def unreported_games(self, division):
        nw = datetime.now() + timedelta(days=3)
        games = filter(lambda x: x.parsed_date() <= nw, self.games)
        # if division == "18u Mens":
        #     assert False, [division, list(games)]
        games = filter(lambda x: not x.reported(), games)
        # if division == "18u Mens":
        #     assert False, [division, list(games)]
        games = list(filter(lambda x: x.division_name == division, games))

        return games

    def schedule(self, tournament_name=None) -> Schedule:
        schedule = Schedule(
            by_team={}, by_division={}, games=[], division_order=DIVISION_AND_ALL
        )
        games: list[Game] = []

        if tournament_name:
            games += self.tournaments[tournament_name].games
        else:
            games = [] + self.games
            for t in self.tournaments.values():
                games += t.games

        for game in games:
            schedule.add_game(game)

        return schedule

    def schedules(self) -> dict[str, Schedule]:
        schedules: dict[str, Schedule] = {}
        schedules["All"] = self.schedule()
        for t in self.tournaments.values():
            if t.name == "Regular Sesaon":
                continue

            if t.name == "Regular Season":
                continue

            name = t.name + " " + t.start_date + "-" + t.end_date
            schedules[name] = t.schedule(tournament_name=t.name)

        return schedules

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
                if d.tournament_name:
                    self.tournaments[d.tournament_name].add_game(d)
                else:
                    self.games.append(d)
        elif isinstance(d, Contact):
            d.organization = self.organizations[d.organization_name]
            self.contacts.append(d)
        elif isinstance(d, Tournament):
            self.tournaments[d.name] = d
