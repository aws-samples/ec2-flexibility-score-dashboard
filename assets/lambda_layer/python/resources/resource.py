from abc import ABCMeta, abstractmethod


class Resource(metaclass=ABCMeta):
    def __init__(self, event_data: dict, event_payload: dict):
        self.hydrate(event_data, event_payload)

    @abstractmethod
    def hydrate(self, event_data: dict, event_payload: dict):
        pass

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()
