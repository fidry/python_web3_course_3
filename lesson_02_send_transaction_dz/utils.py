import json
import os


def get_json(path: str | list[str] | tuple[str]):
    if isinstance(path, (list, tuple)):
        path = os.path.join(*path)
    return json.load(open(path))