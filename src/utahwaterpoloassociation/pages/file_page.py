import glob
import os
from utahwaterpoloassociation.file_data import FileData
from utahwaterpoloassociation.models import Data
from jinja2 import Environment, Template

from .page_base import PageBase


class FilePage(PageBase):
    relative_directory: str
    relative_path: str
    absolute_path: str
    template: str = "page.html.jinja2"

    @classmethod
    def collect(cls, data: Data) -> list["FilePage"]:
        pages = []
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
