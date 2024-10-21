from typing import Any, Type
from utahwaterpoloassociation.pages import PageBase, FilePage
from utahwaterpoloassociation.jinja_env import get_environment
from utahwaterpoloassociation.global_data import get_global_data
from jinja2 import Environment


page_sources: list[Type[PageBase]] = [FilePage]


class Generator:
    env: Environment
    pages: dict[str, PageBase] = {}
    data: dict[str, Any]

    def __init__(self):
        self.data = get_global_data()
        self.env = get_environment(self.data)

    def load_pages(self):
        for src in page_sources:
            for page in src.collect(data=self.data):
                self.pages[page.relative_path] = page

    def render(self):
        for page in self.pages.values():
            page.render_to_path(base="./", env=self.env, data=self.data)
