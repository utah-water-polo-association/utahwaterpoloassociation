from typing import Any
from utahwaterpoloassociation.models import Leauge, Data
import yaml


def process_globals(g) -> Any:
    g["navigation_by_section"] = {}

    for link in g["navigation"]:
        g["navigation_by_section"][link["section"]] = link

    return g


def get_global_data() -> Data:
    league = None
    with open("league.json", "r") as fd:
        league: Leauge = Leauge.model_validate_json(fd.read())

    globals = {}
    with open(file="global.yaml", mode="r") as fd:

        globals = yaml.load(fd, yaml.Loader)
        globals = process_globals(globals)

    return Data(league=league, meta=globals)
