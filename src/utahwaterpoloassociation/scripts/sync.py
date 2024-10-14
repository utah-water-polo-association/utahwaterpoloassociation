import httpx
from pydantic import BaseModel
from typing import Type
import csv
import pickle
from utahwaterpoloassociation.models import (
    Organization,
    Division,
    Location,
    Team,
    Game,
    Leauge,
)

BASE_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT6ytRH8Uqoesk5-A8suLW6OlJ-ucUXgAeTab_c6rIKDSC1SO3Onrj_Tno9koOsPUNIbOuuGAVj_4yw/pub?output=csv"


def from_csv(cls, data):
    results = []
    for row in data:
        kwargs = {}
        for remote_key, local_key in cls.MAP.items():
            if remote_key.startswith("__"):
                kwargs[local_key] = None
            else:
                val = row[remote_key].strip()
                kwargs[local_key] = val

        results.append(cls(**kwargs))

    return results


class SectionConfig(BaseModel):
    label: str
    gid: str
    model: Type[BaseModel]


SECTIONS: list[SectionConfig] = [
    SectionConfig(label="Organizations", gid="0", model=Organization),
    SectionConfig(label="Locations", gid="1642579731", model=Location),
    SectionConfig(label="Divisions", gid="99051020", model=Division),
    SectionConfig(label="Teams", gid="2085958623", model=Team),
    SectionConfig(label="Games", gid="424067115", model=Game),
]


def get_league() -> Leauge:
    league = Leauge()
    for section in SECTIONS:
        print("parsing %s" % (section.label))
        data = httpx.get(BASE_URL + "&gid=" + section.gid, follow_redirects=True)
        reader = csv.DictReader(data.iter_lines())
        items: list[dict[str, str]] = [x for x in reader]
        parsed_items = section.model.from_csv(items)
        for x in parsed_items:
            league.add_data(x)

    return league


if __name__ == "__main__":
    leauge: Leauge = get_league()

    with open("data.pkl", "wb") as file:
        # Dump the data into the file
        pickle.dump(leauge, file, -1)
