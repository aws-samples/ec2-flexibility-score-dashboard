#!/usr/bin/python
# Author: Borja Pérez Guasch <bpguasch@amazon.com>
# License: Apache 2.0
# Summary: module with helper methods to work with dates

from datetime import datetime


def get_timezone():
    """
    Returns information about the current time zone

    :return: current timezone
    """

    return datetime.now().astimezone().tzinfo


def datetime_to_str(date_time: datetime = datetime.now(), datetime_format: str = '%Y-%m-%d') -> str:
    return date_time.strftime(datetime_format)


class TimeWindow:
    """
    Class that represents a time window with a start and an end
    """

    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time

    def before(self, obj) -> bool:
        if type(obj) is datetime:
            return self.end_time < obj

        return self.end_time < obj.start_time

    def contains(self, obj) -> bool:
        if type(obj) is datetime:
            return self.start_time <= obj <= self.end_time

        return self.start_time <= obj.start_time and self.end_time >= obj.end_time

    def after(self, obj) -> bool:
        if type(obj) is datetime:
            return self.start_time > obj

        return self.start_time > obj.end_time
