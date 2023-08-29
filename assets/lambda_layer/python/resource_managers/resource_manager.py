from abc import ABCMeta, abstractmethod
from .libs_finder import *


class ResourceManager(metaclass=ABCMeta):
    def __init__(self, tw: TimeWindow, region: str, credentials: dict = None):
        if credentials is None:
            credentials = {}

        self.credentials = credentials
        self.tw = tw
        self.region = region
        self.resources: dict[str: object] = {}

    @abstractmethod
    def _fetch_cloud_trail_events(self) -> [dict]:
        pass

    @abstractmethod
    def _extract_resources_data_from_events(self, events: [dict]) -> dict[str: object]:
        pass

    def fetch_resources(self) -> dict[str: object]:
        events = self._fetch_cloud_trail_events()
        self.resources = self._extract_resources_data_from_events(events)
        return self.resources
