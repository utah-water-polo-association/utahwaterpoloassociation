import os
import json

from notion_client.helpers import get_id

from notion2md.exceptions import MissingTargetIDError


class Config(object):
    __slots__ = (
        "file_name",
        "target_id",
        "output_path",
        "asset_path",
        "tmp_path",
        "download",
        "unzipped",
        "path_name",
        "page_title",
        "section",
        "web_path",
    )

    def __init__(
        self,
        block_id: str = None,
        block_url: str = None,
        output_filename: str = None,
        output_path: str = None,
        web_path: str = None,
        download: bool = False,
        unzipped: bool = False,
        page_title: str = None,
        section: str = None,
    ):
        self.page_title = page_title
        self.section = section
        if block_url:
            self.target_id = get_id(block_url)
        elif block_id:
            self.target_id = block_id
        else:
            raise MissingTargetIDError

        if output_filename:
            self.file_name = output_filename
        else:
            self.file_name = self.target_id

        self.asset_path: str = os.path.join(output_path, "assets")
        if output_path:
            self.path_name = output_path
            self.output_path = os.path.abspath(output_path)

        else:
            self.path_name = "notion2md-output"
            self.output_path = os.path.join(os.getcwd(), "notion2md-output")

        if download:
            self.download = True
        else:
            self.download = False

        if unzipped:
            self.unzipped = True
            self.tmp_path = os.path.join(self.output_path, "assets")
        else:
            self.unzipped = False
            self.tmp_path = os.path.join(os.getcwd(), "tmp")
        self.web_path = web_path

    def to_dict(self) -> dict:
        return {
            "file_name": self.file_name,
            "target_id": self.target_id,
            "output_path": self.output_path,
            "asset_path": self.asset_path,
            "tmp_path": self.tmp_path,
            "download": self.download,
            "unzipped": self.unzipped,
            "path_name": self.path_name,
            "page_title": self.page_title,
            "section": self.section,
            "web_path": self.web_path,
        }

    @classmethod
    def from_dict(cls, data) -> "Config":
        return cls(**data)
