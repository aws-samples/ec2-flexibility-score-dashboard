from datetime import datetime, timedelta
from .resource_manager import ResourceManager
from .libs_finder import *


class LaunchTemplateManager(ResourceManager):
    def _fetch_cloud_trail_events(self) -> [dict]:
        events = cloudtrail_helpers.fetch_events_by_resource_type(
            RESOURCE_TYPE_LT,
            self.region,
            cloudtrail_helpers.build_events_search_expression(ALL_LT_EVENT_NAMES),
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

            lt_id = event_data['Resources'][1]['ResourceName']

            if lt_id not in resources:
                resources[lt_id] = LaunchTemplate(event_data, event_payload)
            else:
                resources[lt_id].hydrate(event_data, event_payload)

        # SDKs allow for creating an ASG either by specifying the LT id or name. Make the LTs referencable by their name
        lts_by_name = {data.name: data for _, data in resources.items()}
        resources.update(lts_by_name)

        return resources
