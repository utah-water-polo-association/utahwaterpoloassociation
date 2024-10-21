import json
from utahwaterpoloassociation.models import Leauge, Organization


def test_serialization():
    o = Organization(name="test", full_name="Full Name Test")
    leauge = Leauge(organizations={"test": o})

    data = leauge.model_dump(mode="json", serialize_as_any=True)
    raw = json.dumps(data, sort_keys=True)

    new_leauge = Leauge.model_validate_json(raw)

    assert new_leauge == leauge
