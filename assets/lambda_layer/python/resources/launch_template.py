from .resource import Resource
from .libs_finder import *


class LaunchTemplateVersion:
    def __init__(self, event_data: dict, event_payload: dict):
        self.created_at = event_data['EventTime']

        if event_data['EventName'] == EVENT_NAME_CREATE_LT:
            self.version_number = 1
            self.uses_abis = 'InstanceRequirements' in event_payload['requestParameters'][
                'CreateLaunchTemplateRequest']['LaunchTemplateData']
        elif event_data['EventName'] == EVENT_NAME_CREATE_LT_VERSION:
            self.version_number = event_payload['responseElements']['CreateLaunchTemplateVersionResponse'][
                'launchTemplateVersion']['versionNumber']
            self.uses_abis = 'InstanceRequirements' in event_payload['requestParameters'][
                'CreateLaunchTemplateVersionRequest']['LaunchTemplateData']

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class LaunchTemplate(Resource):
    def __init__(self, event_data: dict, event_payload: dict):
        self.id = None
        self.name = None
        self.versions = {}

        super().__init__(event_data, event_payload)

    def hydrate(self, event_data: dict, event_payload: dict):
        self.id = event_data['Resources'][1]['ResourceName']
        self.name = event_data['Resources'][0]['ResourceName']

        if event_data['EventName'] == EVENT_NAME_CREATE_LT:
            self.versions[1] = LaunchTemplateVersion(event_data, event_payload)
            self.versions[DEFAULT] = self.versions[1]
        elif event_data['EventName'] == EVENT_NAME_MODIFY_LT:
            default_version = event_payload['responseElements']['ModifyLaunchTemplateResponse']['launchTemplate'][
                'defaultVersionNumber']

            if default_version in self.versions:
                self.versions[DEFAULT] = self.versions[default_version]
        elif event_data['EventName'] == EVENT_NAME_CREATE_LT_VERSION:
            version = event_payload['responseElements']['CreateLaunchTemplateVersionResponse'][
                'launchTemplateVersion']['versionNumber']
            self.versions[version] = LaunchTemplateVersion(event_data, event_payload)

            # Set this version number as the default if needed
            if event_payload['responseElements']['CreateLaunchTemplateVersionResponse']['launchTemplateVersion'][
             'defaultVersion']:
                self.versions[DEFAULT] = self.versions[version]
