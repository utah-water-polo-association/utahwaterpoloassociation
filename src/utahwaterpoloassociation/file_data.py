import re
import yaml
import markdown
from typing import Any
from pydantic import BaseModel

_yaml_delim = r"(?:---|\+\+\+)"
_yaml = r"(.*?)"
_content = r"\s*(.+)$"
_re_pattern = r"^\s*" + _yaml_delim + _yaml + _yaml_delim + _content
_regex = re.compile(_re_pattern, re.S | re.M)


class FileData(BaseModel):
    attributes: dict[str, Any] = {}
    body: str

    def render_as_markdown(self) -> str:
        return markdown.markdown(self.body)

    @staticmethod
    def read_file(path) -> "FileData":
        """Reads file at path and returns dict with separated frontmatter.
        See read() for more info on dict return value.
        """
        print("path %s" % (path))
        with open(path) as fd:
            file_contents = fd.read()
            body = ""
            result = _regex.search(string=file_contents)

            attributes: dict = {}
            if result:
                attributes = yaml.load(result.group(1).strip(), Loader=yaml.FullLoader)
                body = result.group(2)
            else:
                body = file_contents
            return FileData(
                attributes=attributes,
                body=body,
            )
