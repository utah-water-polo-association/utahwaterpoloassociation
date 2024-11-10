import warnings
import pandas as pd
from typing import Optional
from collections import defaultdict
from pydantic import BaseModel, Field
from ratingslib.ratings.rating import RatingSystem
import ratingslib.ratings as rl
from ratingslib.datasets.parse import parse_pairs_data

from utahwaterpoloassociation.models import GameForAnalysis, Leauge


warnings.simplefilter(action="ignore", category=FutureWarning)

RANKING_METHODS: dict[str, RatingSystem] = {
    "WinLoss": rl.Winloss(normalization=False),
    "Colley": rl.Colley(),
    "Massey": rl.Massey(),
}


class keydefaultdict(defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            ret = self[key] = self.default_factory(key)
            return ret


class DivisionTeam(BaseModel):
    name: str
    games: list[GameForAnalysis] = Field(default_factory=list)
    wins: int = 0
    losses: int = 0

    def add_game(self, game: GameForAnalysis):
        self.games.append(game)
        if self.name == game.winner():
            self.wins += 1
        else:
            self.losses += 1

    def rating(self, team_ratings: dict[str, float]) -> float:
        opponents = list(set(list(map(lambda x: x.opponent(self.name), self.games))))
        rankings = map(lambda x: team_ratings.get(x, 0.5), opponents)
        return (1 + (self.wins - self.losses) / 2) + sum(rankings) / 2 + len(self.games)


class Division(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    name: str
    teams: dict[str, DivisionTeam] = keydefaultdict(lambda x: DivisionTeam(name=x))
    teams_df: Optional[pd.DataFrame] = None
    games_by_week: dict[int, list[GameForAnalysis]] = defaultdict(list)
    games: list[GameForAnalysis] = Field(default_factory=list)
    games_df: Optional[pd.DataFrame] = None

    def add_game(self, game: GameForAnalysis):
        self.games_by_week[game.week].append(game)
        self.teams[game.away_team_name].wins
        self.teams[game.home_team_name].wins

    def ratings_by_week(self):
        self.teams_df = pd.DataFrame([{"Item": x.name} for x in self.teams.values()])
        self.games_df = pd.DataFrame(
            [], columns=["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]
        )

        for wk, games in self.games_by_week.items():
            unique_games: dict[str, GameForAnalysis] = {}
            for game in games:
                unique_games[game.game_id()] = game
                self.teams[game.away_team_name].add_game(game)
                self.teams[game.home_team_name].add_game(game)

            self.games_df = pd.concat(
                [
                    self.games_df,
                    pd.DataFrame(
                        [x.to_df_dict() for x in games],
                        columns=["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"],
                    ),
                ]
            )
            data, _ = parse_pairs_data(self.games_df)

            ranks_by_method = {}
            for key, method in RANKING_METHODS.items():
                out = (
                    method.rate(data, self.teams_df)
                    .sort_values("ranking")
                    .to_dict(orient="records")
                )
                for x in out:
                    x["Item"] = self.teams[x["Item"]]
                ranks_by_method[key] = out
            yield [wk, ranks_by_method, unique_games.values()]


def league_rankings(league: Leauge) -> list[Division]:
    games = [x.for_analysis() for x in league.games]
    divisions: dict[str, Division] = keydefaultdict(lambda x: Division(name=x))
    for game in games:
        divisions[game.division_name].add_game(game)

    return divisions.values()
