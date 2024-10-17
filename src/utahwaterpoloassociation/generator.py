import os
import glob
from typing import Any
from utahwaterpoloassociation.page import Page
from utahwaterpoloassociation.models import Leauge, Data
from jinja2 import Environment, PackageLoader, select_autoescape
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown import Markdown
from markupsafe import Markup
import markdown
import pickle
import yaml


from markdown.treeprocessors import Treeprocessor


class MyTreeprocessor(Treeprocessor):
    def run(self, root):
        return None
        # for element in root.iter("h1"):
        #     element.set(
        #         "class", "text-3xl font-bold leading-tight tracking-tight text-gray-900"
        #     )

        # for element in root.iter("h2"):
        #     element.set(
        #         "class", "text-2xl font-bold leading-tight tracking-tight text-gray-900"
        #     )

        # for element in root.iter("h3"):
        #     element.set(
        #         "class", "text-xl font-bold leading-tight tracking-tight text-gray-900"
        #     )


class MyExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(MyTreeprocessor(md), "mytreeprocessor", 10)


class MarkdownJinja(Extension):
    environment: Environment
    data: Data

    def __init__(self, env: Environment, data: Data):
        self.environment = env
        self.data = data

    def extendMarkdown(self, md: Markdown):
        md.preprocessors.register(
            item=JinjaPreprocessor(md, self.environment, data=self.data),
            name="jinja",
            priority=100,
        )


class JinjaPreprocessor(Preprocessor):
    environment: Environment
    data: Data

    def __init__(self, md: Markdown, env: Environment, data: Data):
        super(JinjaPreprocessor, self).__init__(md)
        self.environment = env
        self.data = data

    def run(self, lines):
        text = "\n".join(lines)
        template = self.environment.from_string(text)
        new_text = template.render(g=self.data)
        return new_text.split("\n")


def makeExtension(env: Environment, data: Data):
    return MarkdownJinja(env=env, data=data)


class Generator:
    env: Environment
    pages: dict[str, Page] = {}
    data: dict[str, Any]

    def __init__(self):

        self.env = Environment(
            loader=PackageLoader("utahwaterpoloassociation"),
            autoescape=select_autoescape(),
        )

        league = None
        with open("league.json", "r") as fd:
            league: Leauge = Leauge.model_validate_json(fd.read())

        globals = {}
        with open(file="global.yaml", mode="r") as fd:

            globals = yaml.load(fd, yaml.Loader)

        self.data = Data(league=league, meta=globals)

        self.env.filters["markdown"] = lambda text: Markup(
            object=markdown.markdown(
                text=text,
                extensions=[
                    makeExtension(env=self.env, data=self.data),
                    MyExtension(),
                    "md_in_html",
                ],
            )
        )

    def load_pages(self):
        pwd = os.getcwd()
        basename = "content"
        for filename in glob.iglob(basename + "/**", recursive=True):
            # relative_directory = root
            if os.path.isdir(filename):
                continue
            if "/assets/" in filename:
                continue
            dir, fname = os.path.split(p=filename)
            dir = dir.replace(basename, "output")
            relative_path = os.path.join(dir, fname)
            page = Page(
                relative_directory=dir,
                relative_path=os.path.join(dir, fname),
                absolute_path=os.path.join(pwd, filename),
            )
            self.pages[relative_path] = page

    def render(self):
        for page in self.pages.values():
            page.render_to_path(base="./", env=self.env, data=self.data)
