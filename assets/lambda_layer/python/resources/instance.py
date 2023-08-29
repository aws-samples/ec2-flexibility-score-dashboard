from .resource import Resource
from .libs_finder import *

NORMALIZATION_TABLE = {
    'nano': 0.25,
    'micro': 0.5,
    'small': 1,
    'medium': 2,
    'large': 4,
    'xlarge': 8,
    '2xlarge': 16,
    '3xlarge': 24,
    '4xlarge': 32,
    '6xlarge': 48,
    '8xlarge': 64,
    '9xlarge': 72,
    '10xlarge': 80,
    '12xlarge': 96,
    '16xlarge': 128,
    '18xlarge': 144,
    '24xlarge': 192,
    '32xlarge': 256,
    '56xlarge': 448,
    '112xlarge': 896
}


class LaunchTemplate:
    def __init__(self, id: str, version: str):
        self.id = id
        self.version = version if version == DEFAULT else int(version)

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class LifecycleEvent:
    def __init__(self, event_data: dict, event_payload: dict):
        self.name = event_data['EventName']
        self.time = event_data['EventTime']

        # Determine if the Instance to which this event belongs, was running before this event and as a result of it
        if event_data['EventName'] == EVENT_NAME_BID_EVICTED:
            self.previously_running = True
            self.currently_running = False
        elif event_data['EventName'] == EVENT_NAME_RUN_INSTANCES:
            self.previously_running = False
            self.currently_running = True
        else:
            self.previously_running = event_payload['previousState']['code'] == EVENT_CODE_RUNNING
            self.currently_running = event_payload['currentState']['code'] in (EVENT_CODE_RUNNING,
                                                                               EVENT_CODE_PENDING)

    def __str__(self):
        return self.__dict__


class InstanceAttrs:
    def __init__(self, event_data: dict, event_payload: dict):
        self.type = None
        self.size = None
        self.arch = None
        self.is_spot = None

        self.hydrate(event_data, event_payload)

    def hydrate(self, event_data: dict, event_payload: dict):
        if 'instanceType' in event_payload:
            self.type = event_payload['instanceType']
            self.size = self.type.split('.')[1]

        if 'architecture' in event_payload:
            self.arch = event_payload['architecture']

        if event_data['EventName'] == EVENT_NAME_RUN_INSTANCES:
            self.is_spot = 'instanceLifecycle' in event_payload and event_payload['instanceLifecycle'] == MARKET_SPOT

    def is_initialised(self):
        """
        Determines if required attributes for calculations have been fetched
        :return: True if required attributes are present, False otherwise
        """

        return self.size is not None

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class Instance(Resource):
    _TAG_KEY_ASG_NAME = 'aws:autoscaling:groupName'
    _TAG_KEY_LT_ID = 'aws:ec2launchtemplate:id'
    _TAG_KEY_LT_VERSION = 'aws:ec2launchtemplate:version'

    # ---------------- GETTERS ---------------- #
    def _get_running_windows(self) -> [TimeWindow]:
        if self._running_windows is None:
            self._calculate_running_windows()

        return self._running_windows

    def _get_vcpu_h(self) -> int:
        if self._vcpu_h is None:
            self._calculate_vcpu_h()

        return self._vcpu_h

    # --------------- PROPERTIES -------------- #
    running_windows = property(_get_running_windows)

    vcpu_h = property(_get_vcpu_h)

    # ------------ PRIVATE METHODS ------------ #
    def _entered_running(self, tw: TimeWindow):
        # Note: lifecycle events are sorted by event time in ascending order, and there no events past the time window
        for event in self.lifecycle_events:
            if event.time >= tw.start_time:
                return event.previously_running

        # If we reach this point, the Instance doesn't have any event during the time window; its last event will
        # tell us if the instance was running before entering the time window
        return self.lifecycle_events[-1].currently_running

    def _calculate_running_windows(self) -> None:
        """
        Uses the list of lifecycle events to calculate the running windows of the Instance.

        For those situations in which the Instance did run during the whole time window, or in which it run from
        the last event until the end of the time window, we won't store the end time of the running window to simplify
        the calculation of the Scaling Score.
        """

        windows: [TimeWindow] = []
        prev_start_time = self._events_time_window.start_time

        # Work only with lifecycle events in the time window
        events_in_tw = [event for event in self.lifecycle_events if self._events_time_window.contains(event.time)]

        # No events during the time window, check if the Instance was running during the whole of it
        if not events_in_tw:
            if self._entered_running(self._events_time_window):
                windows.append(TimeWindow(self._events_time_window.start_time, None))
        # Check if the Instance was running between events, starting from the beginning of the time window
        else:
            for event in events_in_tw:
                if event.previously_running:
                    windows.append(TimeWindow(prev_start_time, event.time))

                prev_start_time = event.time

            # Check if the Instance was running between the last event and the end of the time window
            if events_in_tw[-1].currently_running:
                windows.append(TimeWindow(events_in_tw[-1].time, None))

        self._running_windows = windows

    def _calculate_vcpu_h(self) -> None:
        running_time = 0

        for window in self.running_windows:
            if window.end_time is not None:
                running_time += (window.end_time - window.start_time).seconds
            else:
                running_time += (self._events_time_window.end_time - window.start_time).seconds + 1

        self._vcpu_h = running_time * NORMALIZATION_TABLE[self.attrs.size] // 3600 * 2

    # -------------- INITIALIZER -------------- #
    def __init__(self, event_data: dict, event_payload: dict, tw: TimeWindow):
        self.id = None
        self.launched_at = None
        self.terminated_at = None
        self.asg_name = None
        self.lt = None
        self.attrs = InstanceAttrs(event_data, event_payload)
        self.lifecycle_events: [LifecycleEvent] = []

        self._running_windows = None
        self._vcpu_h = None
        self._events_time_window = tw

        super().__init__(event_data, event_payload)

    # ------------- PUBLIC METHODS ------------ #
    def hydrate(self, event_data: dict, event_payload: dict):
        self.lifecycle_events.append(LifecycleEvent(event_data, event_payload))
        self.attrs.hydrate(event_data, event_payload)

        if 'instanceId' in event_payload:
            self.id = event_payload['instanceId']

        if event_data['EventName'] == EVENT_NAME_RUN_INSTANCES:
            self.launched_at = event_data['EventTime']
        elif event_data['EventName'] in (EVENT_NAME_TERMINATE_INSTANCES, EVENT_NAME_BID_EVICTED):
            self.terminated_at = event_data['EventTime']

        # Explore the tags to try to find the used LT and the ASG to which the Instance has been launched
        if 'tagSet' in event_payload:
            tags = {tag['key']: tag['value'] for tag in event_payload['tagSet']['items']}

            if self._TAG_KEY_ASG_NAME in tags:
                self.asg_name = tags[self._TAG_KEY_ASG_NAME]

            if self._TAG_KEY_LT_ID in tags:
                self.lt = LaunchTemplate(tags[self._TAG_KEY_LT_ID], tags[self._TAG_KEY_LT_VERSION])

    def is_initialised(self):
        """
        Determines if required attributes for calculations have been fetched
        :return: True if required attributes are present, False otherwise
        """

        return self.attrs.is_initialised() and self.launched_at is not None
