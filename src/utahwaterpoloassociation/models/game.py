from pydantic import BaseModel
from typing import Optional, ClassVar
from .csv import from_csv
from .location import Location
from .division import Division
from .team import Team


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
        data = [x for x in data if x.get("date")]
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
        self.location = l.locations.get(self.location_name)

        self.home_team = l.teams["-".join([self.home_team_name, self.division.name])]
        self.away_team = l.teams["-".join([self.away_team_name, self.division.name])]

        if self.winner_name:
            self.winner = l.teams["-".join([self.winner_name, self.division.name])]

        if self.loser_name:
            self.loser = l.teams["-".join([self.loser_name, self.division.name])]
