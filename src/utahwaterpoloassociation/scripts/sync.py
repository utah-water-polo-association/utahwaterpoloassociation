import httpx
import os
import csv
import pprint
from typing import Optional
import json
from slugify import slugify
from utahwaterpoloassociation.models import (
    Leauge,
    SECTIONS,
)
from notion2md.exporter.block import MarkdownExporter
from notion_client import Client
from pydantic import BaseModel

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


class NavItem(BaseModel):
    title: str
    link: str
    navigation: list["NavItem"]


class Page(BaseModel):
    id: str
    title: str
    root: bool = False
    pages: list["Page"] = []
    parent: Optional["Page"]

    @staticmethod
    def from_result(page: dict[any, any], parent=None) -> "Page":
        return Page(
            id=page["id"],
            title=page.get("child_page", {}).get("title", ""),
            parent=parent,
        )

    def add_page(self, page: "Page"):
        self.pages.append(page)

    def slug(self) -> str:
        return "" if self.root else slugify(self.title)

    def path(
        self,
    ) -> str:
        root = self.parent.path() if self.parent else ""

        return root + self.slug() + "/"

    def to_navigation(self) -> NavItem:
        return NavItem(
            title=self.title,
            link=self.path(),
            navigation=[x.to_navigation() for x in self.pages],
        )


def get_pages(parent: Page) -> list[Page]:
    resp = notion_client.blocks.children.list(block_id=parent.id)
    child_pages = list(
        filter(lambda x: x["type"] == "child_page", resp.get("results", []))
    )
    pages = list(map(Page.from_result, child_pages))

    for page in pages:
        page.pages = get_pages(page)
        page.parent = parent

    return pages


def get_page(id: str) -> Page:
    resp = notion_client.blocks.retrieve(block_id=id)
    page = Page.from_result(resp, None)
    page.pages = get_pages(page)

    return page


def export_pages(pages):
    for page in pages:
        print("%s %s" % (page.title, page.path()))
        output_path = page.path()
        if output_path == "/":
            output_path = ""

        me = MarkdownExporter(
            block_id=page.id,
            output_filename="index",
            output_path="content/%s" % (output_path),
            web_path=page.path(),
            download=True,
            unzipped=True,
            token=os.environ["NOTION_TOKEN"],
            page_title=page.title,
            section=page.path(),
        )

        me.export()
        export_pages(page.pages)


def get_content():
    page = get_page(id="12043305db9a8021956ef22e7802e09a")
    page.root = True
    export_pages([page])
    with open("global.json", "w+") as fd:
        data = {"navigation": [x.model_dump() for x in page.to_navigation().navigation]}
        json.dump(data, fd)


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
