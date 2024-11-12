from pydantic import BaseModel
from datetime import datetime
from typing import Optional, ClassVar
from .csv import from_csv
from .location import Location
from .division import Division
from .team import Team


class GameForAnalysis(BaseModel):
    date: datetime
    week: int
    division_name: str
    home_team_name: str
    home_team_score: Optional[float]
    away_team_name: str
    away_team_score: Optional[float]

    def game_id(self) -> str:
        return "%s:%s:%s:%s" % (
            self.date.timestamp(),
            self.division_name,
            self.home_team_name,
            self.away_team_name,
        )

    def to_df_dict(self):
        return {
            "Date": self.date,
            "HomeTeam": self.home_team_name,
            "AwayTeam": self.away_team_name,
            "FTHG": self.home_team_score,
            "FTAG": self.away_team_score,
        }

    def decided(self) -> bool:
        return self.home_team_score and self.away_team_score

    def opponent(self, name: str) -> Optional[str]:
        if name == self.home_team_name:
            return self.away_team_name
        elif name == self.away_team_name:
            return self.home_team_name
        else:
            return None

    def winning_score(self) -> Optional[float]:
        if not self.decided():
            return None

        if self.home_team_score > self.away_team_score:
            return self.home_team_score
        else:
            return self.away_team_score

    def losing_score(self) -> Optional[float]:
        if not self.decided():
            return None

        if self.home_team_score > self.away_team_score:
            return self.away_team_score
        else:
            return self.home_team_score

    def loser(self) -> Optional[str]:
        if not self.decided():
            return None

        if self.home_team_score > self.away_team_score:
            return self.away_team_name
        else:
            return self.home_team_name

    def winner(self) -> Optional[str]:
        if not self.decided():
            return None

        if self.home_team_score > self.away_team_score:
            return self.home_team_name
        else:
            return self.away_team_name


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
        data = [x for x in data if x.get("Date")]
        return from_csv(Game, data)

    def game_id(self) -> str:
        return "%s:%s:%s:%s" % (
            self.parsed_date().timestamp(),
            self.division_name,
            self.home_team_name,
            self.away_team_name,
        )

    def reported(self) -> bool:
        return self.home_team_score and self.away_team_score

    def valid(self):
        return all(
            [
                self.division != "",
                self.away_team_name != "",
                self.home_team_name != "",
            ]
        )

    def parsed_date(self) -> datetime:
        return datetime.strptime(self.date, "%m/%d/%Y")

    def for_analysis(self) -> GameForAnalysis:
        dt = self.parsed_date()
        _, wk, _ = dt.isocalendar()

        return GameForAnalysis(
            date=dt,
            week=wk,
            division_name=self.division_name,
            home_team_name=self.home_team_name,
            home_team_score=(
                float(self.home_team_score) if self.home_team_score else None
            ),
            away_team_name=self.away_team_name,
            away_team_score=(
                float(self.away_team_score) if self.away_team_score else None
            ),
        )

    def hydrate_from_league(self, l: "Leauge"):
        if not self.valid():
            return

        self.division = l.divisions[self.division_name]
        self.location = l.locations.get(self.location_name)

        self.home_team = l.teams["-".join([self.home_team_name, self.division.name])]
        self.away_team = l.teams["-".join([self.away_team_name, self.division.name])]

        if self.winner_name:
            self.winner = l.teams["-".join([self.winner_name, self.division.name])]

        if self.loser_name:
            self.loser = l.teams["-".join([self.loser_name, self.division.name])]
