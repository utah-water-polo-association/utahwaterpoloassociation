import httpx
import os
import csv
from typing import Optional
import json
from slugify import slugify
from utahwaterpoloassociation.models import Leauge
from utahwaterpoloassociation.repos import LEAUGE_CONFIG
from notion2md.exporter.block import MarkdownExporter
from notion_client import Client
from pydantic import BaseModel

from utahwaterpoloassociation.repos import save_league, Leagues

transport = httpx.HTTPTransport(retries=2)
client = httpx.Client(transport=transport)

notion_client = Client(auth=os.environ["NOTION_TOKEN"])

FOOTER_NAV_PAGES = ["Past Seasons"]


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
    section: str = "header"
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
            section="footer" if self.title in FOOTER_NAV_PAGES else "header",
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

        # je = JSONExporter(
        #     block_id=page.id,
        #     output_filename="index",
        #     output_path="content/%s" % (output_path),
        #     web_path=page.path(),
        #     download=True,
        #     unzipped=True,
        #     token=os.environ["NOTION_TOKEN"],
        #     page_title=page.title,
        #     section=page.path(),
        # )

        me.export()
        # je.export()

        export_pages(page.pages)


def get_content():
    page = get_page(id="12043305db9a8021956ef22e7802e09a")
    page.root = True
    export_pages([page])
    with open("global.json", "w+") as fd:
        data = {"navigation": [x.model_dump() for x in page.to_navigation().navigation]}
        json.dump(data, fd)


def get_league(league_id: Leagues) -> Leauge:
    league = Leauge()
    for section in LEAUGE_CONFIG[league_id]:
        print()
        print()
        print("parsing %s %s" % (league_id, section.label))
        print()
        data = client.get(
            section.base_url + "&gid=" + section.gid, follow_redirects=True
        )
        reader = csv.DictReader(data.iter_lines())
        items: list[dict[str, str]] = [x for x in reader]
        print("Sample csv %s" % items[0:2])
        parsed_items = section.model.from_csv(items)
        print("Sample parsed %s" % parsed_items[0:2])
        for x in parsed_items:
            league.add_data(x)

    return league


if __name__ == "__main__":
    # Is mostly static now, so let's not mess with it Leagues.UTAH_SPRING_2024,
    leagues_to_sync = [
        Leagues.UTAH_SPRING_2025,
        Leagues.UTAH_SPRING_2024,
        Leagues.UTAH_FALL_HS_2023,
        Leagues.UTAH_FALL_HS_2024,
    ]
    for league_id in leagues_to_sync:
        leauge: Leauge = get_league(league_id)
        save_league(league_id, league=leauge)

    get_content()
