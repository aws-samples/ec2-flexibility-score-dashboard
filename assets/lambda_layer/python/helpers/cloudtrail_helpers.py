#!/usr/bin/python
# Author: Borja Pérez Guasch <bpguasch@amazon.com>
# License: Apache 2.0
# Summary: module with helper methods to work with CloudTrail

import boto3
import json


class InvalidEvent(Exception):
    pass


def extract_event_payload(event: dict) -> dict:
    """
    Extracts and returns the payload of a CloudTrail event. Raises a InvalidEvent exception if there's an error
    associated to the event.

    :param event: event of which to extract its payload

    :return: payload of the CloudTrail event
    """

    cloudtrail_event = json.loads(event['CloudTrailEvent'])

    # Discard the event if it failed, as it did not incur an Instance state change
    if 'errorCode' in cloudtrail_event:
        raise InvalidEvent()

    return cloudtrail_event


def build_events_search_expression(events: [str]) -> str:
    """
    Builds a search expression that returns only events with the names included in the events argument

    :param events: list of event names to include in the search expression

    :return: search expression
    """

    events = ['EventName == `{}`'.format(event) for event in events]

    return 'Events[?{}][]'.format(' || '.join(events))


def fetch_events_by_resource_type(resource_type: str, region: str, search_exp: str = 'Events[]', credentials=None,
                                  **kwargs) -> [dict]:
    """
    Convenience method that uses boto3 to fetch CloudTrail events of a given resource type

    :param credentials: credentials to perform the operation
    :param resource_type: resource type of which to fetch the events
    :param region: region in which to operate
    :param search_exp: expression used to filter the results
    :param kwargs: additional keyword arguments, used in the API call

    :return: list of CloudTrail events
    """

    if credentials is None:
        credentials = {}

    client = boto3.client('cloudtrail', region_name=region, **credentials)
    paginator = client.get_paginator('lookup_events')

    kwargs.update({
        'LookupAttributes': [
            {
                'AttributeKey': 'ResourceType',
                'AttributeValue': resource_type
            }
        ]
    })

    page_iterator = paginator.paginate(**kwargs)

    return list(page_iterator.search(search_exp))


def fetch_events_by_event_name(event_name: str, region: str, search_exp: str = 'Events[]', credentials: dict = None,
                               **kwargs) -> [dict]:
    """
    Convenience method that uses boto3 to fetch CloudTrail events with a given name

    :param credentials: credentials to perform the operation
    :param event_name: name of the event to fetch
    :param region: region in which to operate
    :param search_exp: expression used to filter the results
    :param kwargs: additional keyword arguments, used in the API call

    :return: list of CloudTrail events
    """

    if credentials is None:
        credentials = {}

    client = boto3.client('cloudtrail', region_name=region, **credentials)
    paginator = client.get_paginator('lookup_events')

    kwargs.update({
        'LookupAttributes': [
            {
                'AttributeKey': 'EventName',
                'AttributeValue': event_name
            }
        ]
    })

    page_iterator = paginator.paginate(**kwargs)

    return list(page_iterator.search(search_exp))
