from slugify import slugify
from pydantic import BaseModel
from typing import ClassVar
from .csv import from_csv


class Division(BaseModel):
    MAP: ClassVar[dict[str, str]] = {
        "Name": "name",
    }
    name: str

    @staticmethod
    def from_csv(data: list[dict]) -> list["Division"]:
        return from_csv(Division, data)

    def __hash__(self) -> int:
        return self.name.__hash__()

    def slug(self) -> str:
        return slugify(self.name.replace("'", ""))
