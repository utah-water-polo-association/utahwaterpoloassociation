import os
from utahwaterpoloassociation.models.models import Data
from utahwaterpoloassociation.services import league_rankings
from jinja2 import Environment, Template

from .page_base import PageBase


class DynamicPage(PageBase):
    output_path: str
    template: str
    path: str

    @classmethod
    def collect(cls, data: Data) -> list["DynamicPage"]:
        pages = []

        page = cls(
            output_path="ratings/index.html",
            template="ranking.html.jinja2",
            path="/ratings/",
        )
        pages.append(page)

        return pages

    @property
    def relative_path(self) -> str:
        return self.output_path

    def __init__(self, output_path: str, template: str, path: str):
        self.output_path = output_path
        self.template = template
        self.path = path

    def render_to_path(self, base: str, env: Environment, data: Data):
        template: Template = env.get_template(name=self.template)

        data: str = template.render(
            p={"attributes": {"title": "Rankings", "path": self.path}},
            g=data,
            league_rankings=league_rankings,
            js_data={"season": list(data.past.keys())[0], "division": ""},
        )
        output_path = os.path.join(base, "output", self.output_path)

        if not os.path.exists(path=os.path.dirname(output_path)):
            os.makedirs(name=os.path.dirname(output_path))

        with open(output_path, "w") as fd:
            fd.write(data)
