import os
import hashlib
from enum import Enum, unique
from typing import Tuple
import json

from utahwaterpoloassociation.models import Leauge

DATA_PATH = "./data"


def data_location(data_key: str) -> str:
    return os.path.join(DATA_PATH, "%s.json" % (data_key))


@unique
class Leagues(Enum):
    UTAH_FALL_HS_2023 = "UTAH_FALL_HS_2023"
    UTAH_SPRING_2024 = "UTAH_SPRING_2024"
    UTAH_FALL_HS_2024 = "UTAH_FALL_HS_2024"
    UTAH_SPRING_2025 = "UTAH_SPRING_2025"


def league_data_key(league: Leagues) -> str:
    return "league_%s" % (league.value)


def hash_data(data: dict[any, any]) -> str:
    raw = json.dumps(data, sort_keys=True)

    return hashlib.sha512(raw).hexdigest()


def get_league(league_id: Leagues) -> Tuple[str, Leauge]:
    with open(data_location(league_data_key(league_id)), "r") as fd:
        return Leauge.model_validate_with_hash(json.load(fd))


def save_league(league_id: Leagues, league: Leauge) -> str:
    hash, data = league.model_dump_with_hash()
    with open(data_location(league_data_key(league_id)), "w+") as fd:
        json.dump(data, fd)

    return hash
