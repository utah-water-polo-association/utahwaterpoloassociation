from pydantic import BaseModel
from typing import ClassVar
from .csv import from_csv
from .game import Game
from .schedule import Schedule, DIVISION_AND_ALL


class Tournament(BaseModel):
    MAP: ClassVar[dict[str, str]] = {
        "Name": "name",
        "Host": "host",
        "Start Date": "start_date",
        "End Date": "end_date",
    }

    name: str
    host: str
    start_date: str
    end_date: str
    games: list["Game"] = []

    @staticmethod
    def from_csv(data: list[dict]) -> list["Tournament"]:
        return from_csv(Tournament, data)

    def key(self) -> str:
        return self.name

    def add_game(self, game: "Game"):
        self.games.append(game)

    def schedule(self, tournament_name=None) -> Schedule:
        schedule = Schedule(
            by_team={}, by_division={}, games=[], division_order=DIVISION_AND_ALL
        )
        games = (g for g in self.games if g.tournament_name == tournament_name)
        for game in games:
            schedule.add_game(game)

        return schedule

    def hydrate_from_league(self, l: "Leauge"):
        return None
