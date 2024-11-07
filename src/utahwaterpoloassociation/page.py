import os
from pydantic import BaseModel
from utahwaterpoloassociation.file_data import FileData
from utahwaterpoloassociation.models.models import Data
from jinja2 import Environment, Template


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
