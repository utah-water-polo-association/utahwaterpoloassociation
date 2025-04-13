from pydantic import BaseModel
from .game import Game

ALL_DIVISION = "All"
DIVISION_ORDER = [
    "HS Varsity Boys",
    "18u Boys",
    "18u Mens",
    "HS Varsity Girls",
    "18u Girls",
    "18u Womens",
    "HS Combined Boys",
    "16u Boys",
    "16u Mens",
    "HS Combined Girls",
    "16u Girls",
    "16u Womens",
    "HS JV Boys",
    "14u Boys",
    "14u Combined",
    "14u Girls",
    "14u Womens",
    "12u Combined",
    "12u Mixed",
    "10u Combined",
    "10u Mixed",
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
