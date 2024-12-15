import glob
import os
import json
from utahwaterpoloassociation.models.models import Data
from jinja2 import Environment, Template

from .page_base import PageBase
from notion2md.config import Config
from utahwaterpoloassociation.notion.convert import BlockConvertor


class JSONPage(PageBase):
    relative_directory: str
    relative_path: str
    absolute_path: str
    template: str = "page.html.jinja2"

    @classmethod
    def collect(cls, data: Data) -> list["JSONPage"]:
        pages = []
        pwd = os.getcwd()
        basename = "content"
        for filename in glob.iglob(basename + "/**", recursive=True):
            # relative_directory = root
            if os.path.isdir(filename):
                continue
            if "/assets/" in filename:
                continue
            if ".json" not in filename:
                continue

            dir, fname = os.path.split(p=filename)
            dir = dir.replace(basename, "output")
            relative_path = os.path.join(dir, fname)
            page = cls(
                relative_directory=dir,
                relative_path=relative_path,
                absolute_path=os.path.join(pwd, filename),
            )
            pages.append(page)

        return pages

    def relative_directory(self) -> str:
        return self.relative_directory

    def relative_path(self) -> str:
        return self.relative_path

    def absolute_path(self) -> str:
        return self.absolute_path

    def __init__(self, relative_directory: str, relative_path: str, absolute_path: str):
        self.relative_directory = relative_directory
        self.relative_path = relative_path
        self.absolute_path = absolute_path

    def output_relative_path(self, format: str = "html") -> str:
        path, _ending = self.relative_path.split(".")
        return path + "." + format

    def render_to_path(self, base: str, env: Environment, data: Data):
        json_data = None
        with open(self.absolute_path) as fd:
            json_data = json.load(fd)

        config = Config.from_dict(json_data["config"])
        converter = BlockConvertor(config)
        body = converter.convert(json_data["blocks"])
        page_title = config.page_title or ""
        page = {
            "body": body,
            "attributes": {
                "title": page_title.title(),
                "section": page_title,
                "path": config.web_path,
            },
        }
        t = fd.attributes.get("template", self.template)
        template: Template = env.get_template(name=t)

        data: str = template.render(p=page, g=data)
        output_path = os.path.join(base, self.output_relative_path())

        if not os.path.exists(path=self.relative_directory):
            os.makedirs(name=self.relative_directory)

        print("rendering input: %s output: %s" % (self.absolute_path, output_path))
        with open(output_path, "w") as fd:
            fd.write(data)
