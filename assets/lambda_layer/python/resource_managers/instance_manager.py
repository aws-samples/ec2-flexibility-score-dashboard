from datetime import datetime, timedelta
from .resource_manager import ResourceManager
from .libs_finder import *


class InstanceManager(ResourceManager):
    def _fetch_cloud_trail_events(self) -> [dict]:
        # Lookup EC2 Instance events and keep only Run, Stop, Start and Terminate
        events = cloudtrail_helpers.fetch_events_by_resource_type(
            RESOURCE_TYPE_INSTANCE,
            self.region,
            cloudtrail_helpers.build_events_search_expression(ALL_INSTANCE_EVENT_NAMES),
            credentials=self.credentials,
            StartTime=datetime.now() - timedelta(MAX_CT_RELATIVE_DAYS_SEARCH),
            EndTime=self.tw.end_time
        )

        # Lookup Spot termination events (those are not included in the EC2 Instance resource type based search)
        events += cloudtrail_helpers.fetch_events_by_event_name(
            EVENT_NAME_BID_EVICTED,
            self.region,
            credentials=self.credentials,
            StartTime=datetime.now() - timedelta(MAX_CT_RELATIVE_DAYS_SEARCH),
            EndTime=self.tw.end_time
        )

        # Sort all the events in ascending order by event time
        return sorted(events, key=lambda e: e['EventTime'])

    def _extract_resources_data_from_events(self, events: [dict]) -> dict[str: object]:
        instances = {}

        for event_data in events:
            try:
                event_payload = cloudtrail_helpers.extract_event_payload(event_data)
            except InvalidEvent:
                continue

            # The structure of the bid evicted event is different, deal with it differently
            if event_data['EventName'] == EVENT_NAME_BID_EVICTED:
                # For every Instance associated to the event...
                for i_id in event_payload['serviceEventDetails']['instanceIdSet']:
                    # Initialise the Instance or hydrate it if we already found an event associated to it
                    if i_id not in instances:
                        instances[i_id] = Instance(event_data, {'instanceId': i_id}, self.tw)
                    else:
                        instances[i_id].hydrate(event_data, {})
            else:
                # For every Instance associated to the event...
                for instance_data in event_payload['responseElements']['instancesSet']['items']:
                    i_id = instance_data['instanceId']

                    # Initialise the Instance or hydrate it if we already found an event associated to it
                    if i_id not in instances:
                        instances[i_id] = Instance(event_data, instance_data, self.tw)
                    else:
                        instances[i_id].hydrate(event_data, instance_data)

        return instances
        
    def fetch_resources(self) -> dict[str: object]:
        events = self._fetch_cloud_trail_events()
        instances = self._extract_resources_data_from_events(events)

        # Discard instances of which we couldn't fetch required attributes and instances terminated before the time window
        instances = {
            i_id: instance for i_id, instance in instances.items()
            if instance.is_initialised() and
            (instance.terminated_at is None or self.tw.contains(instance.terminated_at))
        }

        self.resources = instances

        return instances
