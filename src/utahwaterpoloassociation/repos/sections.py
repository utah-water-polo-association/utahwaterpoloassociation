from pydantic import BaseModel
from typing import Type
from utahwaterpoloassociation.models.organization import Organization
from utahwaterpoloassociation.models.location import Location
from utahwaterpoloassociation.models.division import Division
from utahwaterpoloassociation.models.team import Team
from utahwaterpoloassociation.models.game import Game
from utahwaterpoloassociation.models.contact import Contact
from .leagues import Leagues

LEAGUE_MAIN = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT6ytRH8Uqoesk5-A8suLW6OlJ-ucUXgAeTab_c6rIKDSC1SO3Onrj_Tno9koOsPUNIbOuuGAVj_4yw/pub?output=csv"
LEAGUE_FALL_HS_2023 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQgEqZ3zgCyjZjvFyG-xAe1HOsDU7XzUw3GqPCFJLlr4va9JW474nQBDCfhjkJhnIOIWZHbUFnnjwQO/pub?output=csv"
LEAGUE_SPRING_2024 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSdspx-mD9WlQolmGYGiKTSHkapqSRx-2ZVRjKL6U_5GvV9YYqmm_0sD4gKTVNw5QqgNZ1tklp_N5U5/pub?output=csv"
LEAGUE_FALL_HS_2024 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTH_yp5doUzuYUoTXZxJeeh0fVTV-J6NWALR90xZ_HqQzl-APfQwxZ5m7paFKOWoWtwa_Y9zFj7nB8q/pub?output=csv"
LEAGUE_SPRING_2025 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQVOai3pl4dtMNngXvyDit-bK5_HFK9gwmJ-KICePRXkKhnKxvnInjE5Kzp-Vya2tQdv_UB4Cz9-Rit/pub?output=csv"


class SectionConfig(BaseModel):
    base_url: str
    label: str
    gid: str
    model: Type[BaseModel]


LEAUGE_CONFIG: dict[Leagues, list[SectionConfig]] = {
    Leagues.UTAH_SPRING_2024: [
        SectionConfig(
            base_url=LEAGUE_MAIN, label="Organizations", gid="0", model=Organization
        ),
        SectionConfig(
            base_url=LEAGUE_MAIN, label="Locations", gid="1642579731", model=Location
        ),
        SectionConfig(
            base_url=LEAGUE_SPRING_2024,
            label="Divisions",
            gid="99051020",
            model=Division,
        ),
        SectionConfig(
            base_url=LEAGUE_SPRING_2024, label="Teams", gid="2085958623", model=Team
        ),
        SectionConfig(
            base_url=LEAGUE_SPRING_2024, label="Games", gid="424067115", model=Game
        ),
        SectionConfig(
            base_url=LEAGUE_MAIN, label="Contact Sheet", gid="1058937840", model=Contact
        ),
    ],
    Leagues.UTAH_SPRING_2025: [
        SectionConfig(
            base_url=LEAGUE_MAIN, label="Organizations", gid="0", model=Organization
        ),
        SectionConfig(
            base_url=LEAGUE_MAIN, label="Locations", gid="1642579731", model=Location
        ),
        SectionConfig(
            base_url=LEAGUE_SPRING_2025,
            label="Divisions",
            gid="99051020",
            model=Division,
        ),
        SectionConfig(
            base_url=LEAGUE_SPRING_2025, label="Teams", gid="2085958623", model=Team
        ),
        SectionConfig(
            base_url=LEAGUE_SPRING_2025, label="Games", gid="424067115", model=Game
        ),
        SectionConfig(
            base_url=LEAGUE_MAIN, label="Contact Sheet", gid="1058937840", model=Contact
        ),
    ],
    Leagues.UTAH_FALL_HS_2023: [
        SectionConfig(
            base_url=LEAGUE_MAIN, label="Organizations", gid="0", model=Organization
        ),
        SectionConfig(
            base_url=LEAGUE_MAIN, label="Locations", gid="1642579731", model=Location
        ),
        SectionConfig(
            base_url=LEAGUE_FALL_HS_2023,
            label="Divisions",
            gid="99051020",
            model=Division,
        ),
        SectionConfig(
            base_url=LEAGUE_FALL_HS_2023, label="Teams", gid="2085958623", model=Team
        ),
        SectionConfig(
            base_url=LEAGUE_FALL_HS_2023, label="Games", gid="424067115", model=Game
        ),
        SectionConfig(
            base_url=LEAGUE_MAIN, label="Contact Sheet", gid="1058937840", model=Contact
        ),
    ],
    Leagues.UTAH_FALL_HS_2024: [
        SectionConfig(
            base_url=LEAGUE_MAIN, label="Organizations", gid="0", model=Organization
        ),
        SectionConfig(
            base_url=LEAGUE_MAIN, label="Locations", gid="1642579731", model=Location
        ),
        SectionConfig(
            base_url=LEAGUE_FALL_HS_2024,
            label="Divisions",
            gid="99051020",
            model=Division,
        ),
        SectionConfig(
            base_url=LEAGUE_FALL_HS_2024, label="Teams", gid="2085958623", model=Team
        ),
        SectionConfig(
            base_url=LEAGUE_FALL_HS_2024, label="Games", gid="424067115", model=Game
        ),
        SectionConfig(
            base_url=LEAGUE_MAIN, label="Contact Sheet", gid="1058937840", model=Contact
        ),
    ],
}
