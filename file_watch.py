import json
import os
from typing import TypedDict


class StrongholdData(TypedDict):
    pos: tuple[int, int]
    percentage: float


class StrongholdWatcher:
    def __init__(self, path: str):
        self._cached_stamp = 0
        self.filename = path
        self.data: list[StrongholdData] = []

    def poll(self):
        try:
            stamp = os.stat(self.filename).st_mtime
            if stamp != self._cached_stamp:
                self._cached_stamp = stamp
                with open(self.filename, encoding="utf8") as f:
                    self.data: list[StrongholdData] = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(e)
        return self.data
