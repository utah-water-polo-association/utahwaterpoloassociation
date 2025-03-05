from typing import Any
import os
from utahwaterpoloassociation.models.models import Data, Leauge
from utahwaterpoloassociation.repos import get_league, Leagues
import json


def process_globals(g) -> Any:
    g["navigation_by_link"] = {}

    for link in g["navigation"]:
        g["navigation_by_link"][link["link"]] = link

    g["navigation"][2]["navigation"].append(
        {
            "link": "/report/",
            "navigation": [],
            "section": "header",
            "title": "Score Reporting",
        },
    )

    return g


def get_global_data() -> Data:
    hsh, league = get_league(Leagues.UTAH_SPRING_2025)
    past_data: dict[str, Leauge] = {}
    for league_id in Leagues:
        if league == Leagues.UTAH_SPRING_2025:
            continue

        hsh, league = get_league(league_id)
        past_data[league_id.value] = league

    globals = {}
    with open(file="global.json", mode="r") as fd:

        globals = json.load(fd)
        globals["title"] = "Utah Water Polo Association"
        globals = process_globals(globals)

    globals["php_host"] = os.environ.get(
        "PHP_HOST", "https://utahwaterpoloassociation.com"
    )
    return Data(league=league, meta=globals, past=past_data)
