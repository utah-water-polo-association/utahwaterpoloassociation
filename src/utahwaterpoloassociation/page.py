import os
from contextlib import contextmanager
from pydantic import BaseModel
from utahwaterpoloassociation.file_data import FileData
from utahwaterpoloassociation.models import Data
from jinja2 import Environment, Template
from domonic.html import *


def page_head(p: FileData, g: Data) -> head:
    return head(
        link(rel="apple-touch-icon", sizes="180x180", href="/apple-touch-icon.png"),
        link(rel="icon", type="image/png", sizes="32x32", href="/favicon-32x32.png"),
        link(rel="icon", type="image/png", sizes="16x16", href="/favicon-16x16.png"),
        link(rel="manifest", href="/site.webmanifest"),
        link(rel="stylesheet", href="/style.css"),
        script(src="//unpkg.com/alpinejs", defer=""),
        title(f"{p.attributes.get('title', '')} - {g.meta.get('title', '')}"),
    )


def base_html(content: div, p: FileData, g: Data) -> html:
    return html(
        page_head(p, g), body(div(cls="min-h-full"), cls="h-full"), cls="w-full"
    )


def page_html(p: FileData, g: Data) -> str:
    return ""


class Page(BaseModel):
    relative_directory: str
    relative_path: str
    absolute_path: str
    template: str = "page.html.jinja2"

    def output_relative_path(self, format: str = "html") -> str:
        path, ending = self.relative_path.split(".")
        return path + "." + format

    def render_to_path(self, base: str, env: Environment, data: Data):
        fd: FileData = FileData.read_file(self.absolute_path)

        t = fd.attributes.get("template", self.template)
        template: Template = env.get_template(name=t)

        data: str = template.render(p=fd, g=data)
        output_path = os.path.join(base, self.output_relative_path())

        if not os.path.exists(path=self.relative_directory):
            os.makedirs(name=self.relative_directory)

        print("rendering input: %s output: %s" % (self.absolute_path, output_path))
        with open(output_path, "w") as fd:
            fd.write(data)
