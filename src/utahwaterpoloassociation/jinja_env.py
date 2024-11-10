from utahwaterpoloassociation.models.models import Data
from jinja2 import Environment, PackageLoader, select_autoescape
import markupsafe
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown import Markdown
from markupsafe import Markup
import markdown

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


def get_jinja_env() -> Environment:
    return Environment(
        loader=PackageLoader("utahwaterpoloassociation"),
        autoescape=select_autoescape(),
    )


def get_environment(data: Data) -> Environment:

    env = get_jinja_env()

    def markdown_filter(text):
        text = text.replace("\u2018", "'")  # Left single quote
        text = text.replace("\u2019", "'")  # Right single quote
        text = text.replace("\u201c", '"')  # Left double quote
        text = text.replace("\u201d", '"')  # Right double quote

        return Markup(
            object=markdown.markdown(
                text=text,
                extensions=[
                    makeExtension(env=env, data=data),
                    MyExtension(),
                    "md_in_html",
                ],
            )
        )

    env.filters["markdown"] = markdown_filter

    def directory() -> Markup:
        return markupsafe.Markup(
            env.get_template(name="directory.html.jinja2").render(g=data)
        )

    env.globals["directory"] = directory

    def schedule(season=None):
        league = data.league
        if season:
            league = data.past[season]

        return markupsafe.Markup(
            env.get_template(name="schedule.html.jinja2").render(g=data, league=league)
        )

    env.globals["schedule_fall_high_school"] = schedule
    env.globals["schedule_fall_youth"] = schedule
    env.globals["schedule_spring"] = schedule

    return env
