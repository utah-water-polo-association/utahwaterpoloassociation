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
    # "Massey": rl.Massey(),
}


class keydefaultdict(defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            ret = self[key] = self.default_factory(key)
            return ret


class TeamForRank:
    def __init__(self, name):
        self.name = name
        self.games = []  # List of Game objects
        self.wins = 0
        self.losses = 0
        self.ties = 0
        self.colley_rating = 0.0
        self.sos_rating = 0.0

    def add_game(self, game):
        self.games.append(game)
        if game.score1 == game.score2:  # Tie
            self.ties += 1
        elif game.winner == self:
            self.wins += 1
        else:
            self.losses += 1

    def total_games(self):
        return self.wins + self.losses + self.ties

    def win_percentage(self):
        total = self.total_games()
        return (self.wins + 0.5 * self.ties) / total if total > 0 else 0.0

    def __str__(self):
        if self.ties > 0:
            return f"{self.name} ({self.wins}-{self.losses}-{self.ties})"
        return f"{self.name} ({self.wins}-{self.losses})"


class GameForRank:
    def __init__(self, team1, team2, score1, score2):
        self.team1 = team1
        self.team2 = team2
        self.score1 = score1
        self.score2 = score2

        # Determine winner and loser
        if score1 > score2:
            self.winner = team1
            self.winner_score = score1
            self.loser = team2
            self.loser_score = score2
        elif score2 > score1:
            self.winner = team2
            self.winner_score = score2
            self.loser = team1
            self.loser_score = score1
        else:
            self.winner = None  # Tie
            self.loser = None

        # Calculate margin of victory
        self.margin = abs(score1 - score2)

    def get_opponent(self, team):
        return self.team2 if team == self.team1 else self.team1

    def get_score(self, team):
        return self.score1 if team == self.team1 else self.score2


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


def solve_linear_system(C, b):
    """
    Solve the linear system Cx = b using Gaussian elimination
    This is a simple implementation without using NumPy
    """
    n = len(b)
    # Create augmented matrix [C|b]
    augmented = [row[:] + [b[i]] for i, row in enumerate(C)]

    # Gaussian elimination (forward elimination)
    for i in range(n):
        # Find pivot
        max_row = i
        for k in range(i + 1, n):
            if abs(augmented[k][i]) > abs(augmented[max_row][i]):
                max_row = k

        # Swap rows if needed
        if max_row != i:
            augmented[i], augmented[max_row] = augmented[max_row], augmented[i]

        # Eliminate below
        for k in range(i + 1, n):
            factor = augmented[k][i] / augmented[i][i]
            for j in range(i, n + 1):
                augmented[k][j] -= factor * augmented[i][j]

    # Back substitution
    x = [0] * n
    for i in range(n - 1, -1, -1):
        x[i] = augmented[i][n]
        for j in range(i + 1, n):
            x[i] -= augmented[i][j] * x[j]
        x[i] /= augmented[i][i]

    return x


def calculate_sos_from_colley(teams: list[TeamForRank]):
    """
    Calculate strength of schedule based on opponents' Colley ratings
    and adjust for margin of victory
    """
    for team in teams:
        if not team.games:
            team.sos_rating = 0.0
            continue

        total_opponent_rating = 0.0
        total_weight = 0.0

        for game in team.games:
            opponent = game.get_opponent(team)
            opponent_rating = opponent.colley_rating

            # Apply margin of victory adjustment
            if game.winner == team:
                # Winner gets slight bonus for margin (capped)
                margin_factor = 1.0 + min(game.margin * 0.01, 0.3)
            elif game.winner == opponent:
                # Loser gets slight penalty but smaller for close games
                margin_factor = max(1.0 - game.margin * 0.005, 0.7)
            else:  # Tie
                margin_factor = 1.0

            weight = margin_factor
            total_opponent_rating += opponent_rating * weight
            total_weight += weight

        # Calculate weighted average of opponent ratings
        team.sos_rating = (
            total_opponent_rating / total_weight if total_weight > 0 else 0.0
        )


def calculate_colley_ratings(teams: list[TeamForRank]) -> list[TeamForRank]:
    """
    Calculate team ratings using the Colley Method
    """
    n = len(teams)

    # Create map of teams to indices
    team_indices = {team.name: i for i, team in enumerate(teams)}

    # Initialize Colley matrix C and right-hand vector b
    C = [[0 for _ in range(n)] for _ in range(n)]
    b = [0 for _ in range(n)]

    # Fill diagonal elements of C with 2 + number of games played
    for i, team in enumerate(teams):
        C[i][i] = 2 + team.total_games()

    # Fill off-diagonal elements and b vector
    for team in teams:
        i = team_indices[team.name]
        # Start with 1 + (wins - losses)/2
        b[i] = 1 + (team.wins - team.losses) / 2

        # For each game, update C matrix
        for game in team.games:
            opponent = game.get_opponent(team)
            j = team_indices[opponent.name]
            C[i][j] -= 1

    # Solve the system Cr = b for ratings r
    ratings = solve_linear_system(C, b)

    # Assign ratings to teams
    for i, team in enumerate(teams):
        team.colley_rating = ratings[i]

    # Calculate strength of schedule based on opponents' Colley ratings
    calculate_sos_from_colley(teams)

    return sorted(teams, key=lambda x: x.colley_rating, reverse=True)


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

    def ratings_by_week_new(self):
        teams = [TeamForRank(x.name) for x in self.teams.values()]
        teams_by_name = {x.name: x for x in teams}
        for wk, games in self.games_by_week.items():
            for game in games:
                if not game.decided():
                    continue
                game_for_rank = GameForRank(
                    teams_by_name[game.away_team_name],
                    teams_by_name[game.home_team_name],
                    game.away_team_score,
                    game.home_team_score,
                )
                teams_by_name[game.away_team_name].add_game(game_for_rank)
                teams_by_name[game.home_team_name].add_game(game_for_rank)

            yield [wk, calculate_colley_ratings(teams)]

    def ratings_by_week(self):
        self.teams_df = pd.DataFrame([{"Item": x.name} for x in self.teams.values()])
        self.games_df = pd.DataFrame(
            [], columns=["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]
        )

        for wk, games in self.games_by_week.items():
            unique_games: dict[str, GameForAnalysis] = {}
            for game in games:
                if not game.decided():
                    continue
                unique_games[game.game_id()] = game
                self.teams[game.away_team_name].add_game(game)
                self.teams[game.home_team_name].add_game(game)

            self.games_df = pd.concat(
                [
                    self.games_df,
                    pd.DataFrame(
                        [x.to_df_dict() for x in games if game.decided()],
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
    for tournament in league.tournaments.values():
        games += [x.for_analysis() for x in tournament.games]

    divisions: dict[str, Division] = keydefaultdict(lambda x: Division(name=x))
    for game in games:
        divisions[game.division_name].add_game(game)

    return divisions.values()
