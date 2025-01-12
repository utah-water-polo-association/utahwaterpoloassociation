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

    def short_name(self) -> str:
        parts = self.name.split(" ")
        age = parts[0]
        kind = parts[1]
        if age != "HS":
            age = int(age.replace("u", ""))
        return f"{age}{kind[0]}"

    def __hash__(self) -> int:
        return self.name.__hash__()

    def slug(self) -> str:
        return slugify(self.name.replace("'", ""))
