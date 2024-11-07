from typing import Any
from utahwaterpoloassociation.models.models import Data
from utahwaterpoloassociation.repos import get_league, Leagues
import json


def process_globals(g) -> Any:
    g["navigation_by_link"] = {}

    for link in g["navigation"]:
        g["navigation_by_link"][link["link"]] = link

    return g


def get_global_data() -> Data:
    league = get_league(Leagues.UTAH_SPRING_2024)

    globals = {}
    with open(file="global.json", mode="r") as fd:

        globals = json.load(fd)
        globals["title"] = "Utah Water Polo Association"
        globals = process_globals(globals)

    return Data(league=league, meta=globals)
