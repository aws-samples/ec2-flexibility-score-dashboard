from enum import Enum
from .resource import Resource
from .libs_finder import *


class LaunchTemplate:
    def __init__(self, data: dict):
        self.id = data['launchTemplateId'] if 'launchTemplateId' in data else data['launchTemplateName']
        self.version = data['version'] if data['version'] == DEFAULT else int(data['version'])

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class Overrides:
    def __init__(self, event_payload: dict):
        self.uses_abis = False
        self.instance_count = None

        if 'mixedInstancesPolicy' in event_payload['requestParameters'] and 'overrides' in event_payload[
         'requestParameters']['mixedInstancesPolicy']['launchTemplate']:
            instance_count = 0

            for override in event_payload['requestParameters']['mixedInstancesPolicy']['launchTemplate'][
             'overrides']:
                if 'instanceRequirements' in override:
                    self.uses_abis = True
                elif 'instanceType' in override:
                    instance_count += 1

            if instance_count != 0:
                self.instance_count = instance_count

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class ASG(Resource):
    def __init__(self, event_data: dict, event_payload: dict):
        self.name = None
        self.created_at = None
        self.deleted_at = None
        self.lt = None
        self.sp = None
        self.overrides = Overrides(event_payload)

        super().__init__(event_data, event_payload)

    def hydrate(self, event_data: dict, event_payload: dict):
        if event_data['EventName'] == EVENT_NAME_CREATE_ASG:
            self.created_at = event_data['EventTime']
        elif event_data['EventName'] == EVENT_NAME_DELETE_ASG:
            self.deleted_at = event_data['EventTime']

        self.name = event_data['Resources'][0]['ResourceName']
        self.overrides = Overrides(event_payload)
        self.lt = None if 'mixedInstancesPolicy' not in event_payload['requestParameters'] else LaunchTemplate(
            event_payload['requestParameters']['mixedInstancesPolicy']['launchTemplate'][
                'launchTemplateSpecification']
        )
