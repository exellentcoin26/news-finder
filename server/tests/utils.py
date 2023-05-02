from typing import Any
from json import dumps, loads


def compare_json(expected: Any, actual: Any) -> bool:
    actual = dumps(actual)
    return loads(expected) == loads(actual)
