from pydantic import BaseModel
from datetime import datetime
from typing import Optional, ClassVar
from time import strftime, strptime, struct_time
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
        "Tournament": "tournament_name",
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
    tournament_name: Optional[str] = None

    @staticmethod
    def from_csv(data: list[dict]) -> list["Game"]:
        data = [x for x in data if x.get("Date")]
        return from_csv(Game, data)

    def key(self) -> str:
        return "%s-%s-%s-%s" % (
            self.away_team_name,
            self.home_team_name,
            self.away_team_score,
            self.home_team_score,
        )

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
                self.date and len(self.date) <= 15,
                self.division_name not in ("1", "2", "3", "4", "5"),
                self.division_name != "",
                self.division_name is not None,
                self.away_team_name != "",
                self.away_team_name not in ("1", "2", "3", "4", "5"),
                self.home_team_name != "",
                self.home_team_name not in ("1", "2", "3", "4", "5"),
            ]
        )

    def parsed_date(self) -> datetime:
        return datetime.strptime(self.date, "%m/%d/%Y")

    def parsed_time(self) -> struct_time | None:
        if self.time == "":
            return None

        return strptime(self.time, "%I:%M:%S %p")
        # return datetime.strptime(self.time, "%m/%d/%Y")

    def short_date_format(self) -> str:
        return datetime.strftime(self.parsed_date(), "%-m/%-d")

    def short_time_format(self) -> struct_time | None:
        if not self.parsed_time():
            return ""

        return strftime("%-I:%M %p", self.parsed_time())
        # return datetime.strptime(self.time, "%m/%d/%Y")

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

        home_team_score, away_team_score = map(
            lambda x: float(x) if x else None,
            [self.home_team_score, self.away_team_score],
        )

        if home_team_score and away_team_score:
            if not self.winner_name and home_team_score > away_team_score:
                self.winner_name = self.home_team_name
                self.loser_name = self.away_team_name

            if not self.loser_name and away_team_score > home_team_score:
                self.loser_name = self.away_team_name
                self.winner_name = self.home_team_name

        if self.winner_name:
            self.winner = l.teams["-".join([self.winner_name, self.division.name])]

        if self.loser_name:
            self.loser = l.teams["-".join([self.loser_name, self.division.name])]
