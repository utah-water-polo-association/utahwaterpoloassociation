import csv
import sys
import pprint
from collections import defaultdict
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ratingslib.ratings.rating import RatingSystem
import ratingslib.ratings as rl
from ratingslib.datasets.parse import parse_pairs_data
import pandas as pd

SPRING_2023_HS = "./data/2023_uwpa_hs_schedule.csv"

RANKING_METHODS: dict[str, RatingSystem] = {
    "WinLoss": rl.Winloss(normalization=False),
    "Colley": rl.Colley(),
    "Massey": rl.Massey(),
    "Keener": rl.Keener(normalization=False),
    "OffenseDefense": rl.OffenseDefense(tol=0.0001),
}


class Game(BaseModel):
    id: str
    week: int
    game: int
    game_date: datetime
    week_day: str
    location: str
    home_team: str
    away_team: str
    divison: str
    home_team_score: float
    away_team_score: float

    @staticmethod
    def transform_to_df(data: list[dict]) -> pd.DataFrame:
        return pd.DataFrame(
            data, columns=["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]
        )

    def to_dataframe_dict(self) -> dict[any, any]:
        return {
            "Date": self.game_date,
            "HomeTeam": self.home_team,
            "AwayTeam": self.away_team,
            "FTHG": self.home_team_score,
            "FTAG": self.away_team_score,
        }

    def from_row(row: list[str]) -> Optional["Game"]:
        date_time = "%s 2023 %s" % (row[2], row[5])
        if row[10] == "Canceled":
            return None
        if "-" not in row[10]:
            return None
        if "W-L" == row[10]:
            return None
        if "L-W" == row[10]:
            return None

        home_score, away_score = map(float, row[10].split("-"))
        return Game(
            id=row[6],
            week=int(row[0].replace("WEEK ", "")),
            game=int(row[1]),
            game_date=datetime.strptime(date_time, "%B %d %Y %I:%M %p"),
            week_day=row[3],
            location="",
            home_team=row[7],
            away_team=row[8],
            home_team_score=home_score,
            away_team_score=away_score,
            divison=row[9],
        )


# WEEK	League ID	DATE	DAY	LOCATION	TIME	GAME ID	HOME (DARK CAPS)	AWAY (WHITE CAPS)	DIVISION	RESULT

# [0: 'WEEK 1', 1: '1', 2: 'August 26', 3: 'SATURDAY', 4: 5'8:00 AM', 6: 'HSJVB GM8', 7: 'Skyline', 8:'Kearns', 9: 'JV Boys', 10: '4-9']


if __name__ == "__main__":
    with open(SPRING_2023_HS, "r") as fd:
        reader = csv.reader(fd)
        games: list[Game] = []
        games_by_week: dict[int, list[Game]] = defaultdict(lambda: defaultdict(list))
        rankings_by_week: dict[any, any] = {}
        games_by_division: dict[str, pd.DataFrame] = {}
        ratings_by_division: dict[str, RatingSystem] = defaultdict(lambda: rl.Colley())
        _teams_by_division: dict[str, list[str]] = defaultdict(list)
        teams_by_division: dict[str, pd.DataFrame] = defaultdict(
            lambda: pd.DataFrame([])
        )

        for b in reader:
            if "WEEK " not in b[0]:
                continue
            gm = Game.from_row(b)
            if not gm:
                continue
            games.append(gm)

        games = sorted(games, key=lambda x: x.game_date)

        for gm in games:
            week = gm.game_date.isocalendar()[1]
            games_by_week[week][gm.divison].append(gm)
            _teams_by_division[gm.divison].append(gm.away_team)
            _teams_by_division[gm.divison].append(gm.home_team)
            if week not in rankings_by_week:
                rankings_by_week[week] = {}

            if gm.divison not in rankings_by_week[week]:
                rankings_by_week[week][gm.divison] = {
                    key: {} for key in RANKING_METHODS.keys()
                }

        for division, teams in _teams_by_division.items():
            teams = list(set(teams))
            teams_by_division[division] = pd.DataFrame([{"Item": x} for x in teams])
            games_by_division[division] = pd.DataFrame(
                [], columns=["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]
            )
        weeks: list[int] = sorted(games_by_week.keys())

        for week in weeks:
            for division, games in games_by_week[week].items():
                # if division != "Varsity Boys":
                #     continue
                games_by_division[division] = pd.concat(
                    [
                        Game.transform_to_df([x.to_dataframe_dict() for x in games]),
                        games_by_division[division],
                    ]
                )
                data, _ = parse_pairs_data(games_by_division[division])

                for key, method in RANKING_METHODS.items():
                    out = (
                        method.rate(data, teams_by_division[division])
                        .sort_values("ranking")
                        .to_dict(orient="records")
                    )
                    rankings_by_week[week][division][key] = out

            w = csv.writer(sys.stdout)
            for week, data in rankings_by_week.items():
                for division, data in data.items():
                    for key, ratings in data.items():
                        for record in ratings:
                            w.writerow(
                                [
                                    week,
                                    division,
                                    key,
                                    record["Item"],
                                    record["ranking"],
                                    record["rating"],
                                ]
                            )
