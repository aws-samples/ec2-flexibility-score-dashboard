from datetime import datetime, timedelta
from .resource_manager import ResourceManager
from .libs_finder import *


class ASGManager(ResourceManager):
    def _fetch_cloud_trail_events(self) -> [dict]:
        events = cloudtrail_helpers.fetch_events_by_resource_type(
            RESOURCE_TYPE_ASG,
            self.region,
            cloudtrail_helpers.build_events_search_expression(ALL_ASG_EVENT_NAMES),
            credentials=self.credentials,
            StartTime=datetime.now() - timedelta(MAX_CT_RELATIVE_DAYS_SEARCH),
            EndTime=self.tw.end_time
        )

        # Sort all the events in ascending order by event time
        return sorted(events, key=lambda e: e['EventTime'])

    def _extract_resources_data_from_events(self, events: [dict]) -> dict[str: object]:
        resources = {}

        for event_data in events:
            try:
                event_payload = cloudtrail_helpers.extract_event_payload(event_data)
            except InvalidEvent:
                continue

            asg_name = event_data['Resources'][0]['ResourceName']

            if asg_name not in resources:
                resources[asg_name] = ASG(event_data, event_payload)
            else:
                resources[asg_name].hydrate(event_data, event_payload)

        return resources

    def _fetch_sp_cloud_trail_events(self) -> [dict]:
        events = cloudtrail_helpers.fetch_events_by_resource_type(
            RESOURCE_TYPE_SP,
            self.region,
            cloudtrail_helpers.build_events_search_expression(ALL_SP_EVENT_NAMES),
            credentials=self.credentials,
            StartTime=datetime.now() - timedelta(MAX_CT_RELATIVE_DAYS_SEARCH),
            EndTime=self.tw.end_time
        )

        # Sort all the events in ascending order by event time
        return sorted(events, key=lambda e: e['EventTime'])

    def _extract_sp_data_from_events(self, events: [dict]) -> dict[str: str]:
        sp = {}

        for event_data in events:
            try:
                event_payload = cloudtrail_helpers.extract_event_payload(event_data)
            except InvalidEvent:
                continue

            params = event_payload['requestParameters']

            if event_data['EventName'] == EVENT_NAME_DELETE_SP:
                sp[params['autoScalingGroupName']] = None
            else:
                sp[params['autoScalingGroupName']] = params['policyType']

        return sp

    def fetch_resources(self) -> dict[str: object]:
        events = self._fetch_cloud_trail_events()
        asg_data = self._extract_resources_data_from_events(events)

        # Discard ASGs deleted before the time window
        asg_data = {
            name: asg for name, asg in asg_data.items()
            if asg.deleted_at is None or self.tw.contains(asg.deleted_at)
        }

        # Fetch scaling policies events
        events = self._fetch_sp_cloud_trail_events()
        sps = self._extract_sp_data_from_events(events)

        # Assign each ASG its scaling policy
        for asg_name, sp in sps.items():
            if asg_name in asg_data:
                asg_data[asg_name].scaling_policy = sp

        self.resources = asg_data

        return asg_data
