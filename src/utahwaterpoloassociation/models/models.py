from pydantic import BaseModel
from typing import Any
from .leauge import Leauge


class Data(BaseModel):
    league: Leauge
    past: dict[str, Leauge] = {}
    meta: dict[str, Any]
