from abc import ABC, abstractmethod
from utahwaterpoloassociation.models.models import Data
from jinja2 import Environment


class PageBase(ABC):

    @classmethod
    @abstractmethod
    def collect(cls, data: Data) -> list["PageBase"]: ...

    @abstractmethod
    def relative_directory(self) -> str: ...

    @abstractmethod
    def relative_path(self) -> str: ...

    @abstractmethod
    def absolute_path(self) -> str: ...

    @abstractmethod
    def render_to_path(self, base: str, env: Environment, data: Data) -> None: ...
