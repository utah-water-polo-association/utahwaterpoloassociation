from typing import Any
from utahwaterpoloassociation.models import Leauge, Data
import json


def process_globals(g) -> Any:
    g["navigation_by_link"] = {}

    for link in g["navigation"]:
        g["navigation_by_link"][link["link"]] = link

    return g


def get_global_data() -> Data:
    league = None
    with open("league.json", "r") as fd:
        league: Leauge = Leauge.model_validate_json(fd.read())

    globals = {}
    with open(file="global.json", mode="r") as fd:

        globals = json.load(fd)
        globals["title"] = "Utah Water Polo Association"
        globals = process_globals(globals)

    return Data(league=league, meta=globals)
