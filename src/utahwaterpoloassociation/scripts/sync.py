import httpx
import os
import csv
import json
from utahwaterpoloassociation.models import (
    Leauge,
    SECTIONS,
)
from notion2md.exporter.block import MarkdownExporter
from notion_client import Client

BASE_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT6ytRH8Uqoesk5-A8suLW6OlJ-ucUXgAeTab_c6rIKDSC1SO3Onrj_Tno9koOsPUNIbOuuGAVj_4yw/pub?output=csv"

notion_client = Client(auth=os.environ["NOTION_TOKEN"])


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


def get_content():
    resp = notion_client.blocks.children.list(
        block_id="12043305db9a8021956ef22e7802e09a"
    )
    pages = list(filter(lambda x: x["type"] == "child_page", resp.get("results", [])))
    for page in pages:
        page_title = page.get("child_page", {}).get("title", "").lower()
        print("downloading %s" % (page_title))

        me = MarkdownExporter(
            block_id=page["id"],
            output_filename="index",
            output_path="content/%s" % (page_title),
            download=True,
            unzipped=True,
            token=os.environ["NOTION_TOKEN"],
            page_title=page_title,
            section=page_title,
        )

        me.export()


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
    data = leauge.model_dump(mode="json", serialize_as_any=True)
    raw = json.dumps(data, sort_keys=True)
    with open("league.json", "w") as file:
        # Dump the data into the file
        file.write(raw)

    get_content()
