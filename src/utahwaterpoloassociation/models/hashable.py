import json
from pydantic import BaseModel
from typing import Any, Tuple
import hashlib


def hash_data(data: dict[any, any]) -> str:
    raw = json.dumps(data, sort_keys=True)

    return hashlib.sha512(raw).hexdigest()


class Hashable(BaseModel):

    def hash(self, data=None) -> str:
        data = data or super().model_dump(mode="json", serialize_as_any=True)
        raw = json.dumps(data, sort_keys=True)
        return hashlib.sha512(bytes(raw, "utf-8")).hexdigest()

    def model_dump_with_hash(self) -> Tuple[str, dict[str, Any]]:
        data = super().model_dump(mode="json", serialize_as_any=True)
        hash = self.hash(data)
        return (
            hash,
            {
                "hash": hash,
                "data": data,
            },
        )

    @classmethod
    def model_validate_with_hash(cls, obj: Any, **kwargs) -> Tuple[str, Any]:
        hash = obj["hash"]
        data = obj["data"]
        return (hash, cls.model_validate(data, **kwargs))
