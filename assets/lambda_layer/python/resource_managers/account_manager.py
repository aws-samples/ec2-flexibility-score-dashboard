import uuid

from threading import Thread
from botocore.exceptions import ClientError
from .libs_finder import *
from .instance_manager import InstanceManager
from .launch_template_manager import LaunchTemplateManager
from .asg_manager import ASGManager

_ORG_NOT_USED_EXCEPTION = 'AWSOrganizationsNotInUseException'
_ROUND_DECIMALS = 2

accounts = {}


class AccountResourcesFetcher(Thread):
    _ROLE_ARN_FORMAT = 'arn:aws:iam::{}:role/{}'

    def __init__(self, account: Account, tw: TimeWindow):
        super().__init__(name=account.id)
        self.tw = tw
        self.account = account

    def _get_credentials(self) -> dict:
        """
        If the account is not the main in the organization, assume a role in the member account to make requests

        :return: dictionary with credentials to perform requests in the account
        """

        role_name = os.environ['ORGS_IAM_ROLE']

        return None if self.account.is_main else sts_helpers.assume_role(self._ROLE_ARN_FORMAT.format(self.account.id,
                                                                                                      role_name))

    def run(self):
        # Get temporary credentials to access AWS resources
        credentials = self._get_credentials()

        # Get the list of enabled regions in the account
        regions = ec2_helpers.describe_regions(self.account.id, credentials)

        print(f'({self.name}) fetching resources...')

        instances = {}
        lt = {}
        asg = {}

        # Fetch resources in all regions
        for region in regions:
            instances.update(InstanceManager(self.tw, region, credentials).fetch_resources())
            lt.update(LaunchTemplateManager(self.tw, region, credentials).fetch_resources())
            asg.update(ASGManager(self.tw, region, credentials).fetch_resources())

        self.account.set_resources(instances, lt, asg)

        print(f'({self.name}) done fetching.')


def _fetch_accounts():
    global accounts

    print('Getting the list of accounts in the organization...')

    try:
        account_data = organizations_helpers.list_organization_accounts()
        main_account_id = organizations_helpers.describe_organization()['MasterAccountId']

        # Add an extra field indicating whether the account is the main in the organization
        for data in account_data:
            data['isMain'] = data['Id'] == main_account_id
    except ClientError as e:
        # Organizations not enabled, treat the account as an organization without invited accounts
        if e.response['Error']['Code'] == _ORG_NOT_USED_EXCEPTION:
            account_data = [{'Id': sts_helpers.get_caller_identity()['Account'], 'isMain': True}]
        else:
            raise Exception(f'Error getting the list of accounts: {e}')

    accounts = {data['Id']: Account(data) for data in account_data}


def fetch_resources(tw: TimeWindow):
    threads = []

    # Fetch account resources in parallel
    for _, account in accounts.items():
        threads.append(AccountResourcesFetcher(account, tw))
        threads[-1].start()

    # Wait until all the threads have executed
    for thread in threads:
        thread.join()


def _weight_scores(metrics: dict) -> dict:
    """
    Weights the score values from different days to return a single value per score in the time range

    :param metrics: metric values per account for a list of days in the format:

    account_id_1:
        metric_name_1:
           day_1: value
           day_2: value
        metric_name_2:
           day_1: value
           day_2: value

    :return: dictionary with weighted score values in the format:

    account_id_1:
        metric_name_1: value
        metric_name_2: value
    account_id_2:
        metric_name_1: value
        metric_name_2: value
    """

    weighted_scores = {a_id: {} for a_id in metrics}

    for a_id in metrics:
        # First calculate the total vCPU hours in the time window
        total_vcpu_h = int(sum([value for day, value in metrics[a_id][CW_METRIC_NAME_VCPU_H].items()]))

        # Calculate the wighted component values adding the products between the daily vCPU hours and component
        # and dividing by the total vCPU hours
        weighted_scores[a_id] = {
            metric_name: round(sum([
                metrics[a_id][metric_name][day] *
                metrics[a_id][CW_METRIC_NAME_VCPU_H][day]

                # Ensure that there are metric values on that day for both the vCPU hours and the metric being calculated
                for day in metrics[a_id][CW_METRIC_NAME_VCPU_H] if day in metrics[a_id][metric_name]
            ]) / total_vcpu_h, _ROUND_DECIMALS) if total_vcpu_h != 0 else 0

            for metric_name in ALL_CW_METRICS - {CW_METRIC_NAME_VCPU_H}
        }

        # Add the total vCPU hours to the account metrics
        weighted_scores[a_id][CW_METRIC_NAME_VCPU_H] = total_vcpu_h

        # Calculate the Flexibility Score
        weighted_scores[a_id][SCORE_FLEXIBILITY] = round(sum([
            weighted_scores[a_id][score_name] * score_weight
            for score_name, score_weight in ALL_SCORES.items() if score_name in weighted_scores[a_id]
        ]), _ROUND_DECIMALS)

    return weighted_scores


def fetch_scores(start_time, end_time, account_ids=None, metric_names=None) -> dict:
    """
    Retrieves account metrics from CloudWatch and calculates their weighted values in the time frame

    :param start_time: start of the time window to get metrics
    :param end_time: end of the time window to get metrics
    :param account_ids: list of account ids of which to get metrics
    :param metric_names: list of metrics to get

    :return: dictionary containing the weighted metrics in the time frame in the following format:

    account_id_1:
        metric_name_1: value
        metric_name_2: value
    account_id_2:
        metric_name_1: value
        metric_name_2: value
    """

    # If an id is not specified, get the metrics for all accounts
    if account_ids is None:
        account_ids = list(accounts.keys())

    # If metrics are not specified, get all the metrics
    if metric_names is None:
        metric_names = ALL_CW_METRICS
    else:
        # Ensure we retrieve the vCPU hours, since it's needed for the weighted calculations
        metric_names.append(CW_METRIC_NAME_VCPU_H)
        metric_names = set(metric_names)

    queries = [
        {
            'Id': f'a_{str(uuid.uuid4()).replace("-", "_")}',
            'Label': f'{a_id}_{metric}',
            'MetricStat': {
                'Metric': {
                    'Namespace': CW_NAMESPACE,
                    'MetricName': metric,
                    'Dimensions': [
                        {
                            'Name': CW_DIMENSION_NAME_ACCOUNT_ID,
                            'Value': a_id
                        },
                    ]
                },
                'Period': CW_METRIC_PERIOD,
                'Stat': 'Average',
            }
        }

        for a_id in account_ids for metric in ALL_CW_METRICS
    ]

    response = cloudwatch_helpers.get_metric_data(start_time, end_time, queries)
    metrics = {a_id: {name: {} for name in metric_names} for a_id in account_ids}

    # Generate a dictionary with the following format:
    # account_id_1:
    #   metric_name_1:
    #       day_1: value
    #       day_2: value
    #   metric_name_2:
    #       day_1: value
    #       day_2: value

    for result in response['MetricDataResults']:
        account_id = result['Label'].split('_')[0]
        metric_name = result['Label'].split('_')[1]

        # We have requested the most recent data points, so these come sorted by date in ascending mode.
        # Traverse the results in reverse so that the last dictionary update keeps the most recent metric value
        for i in range(len(result['Timestamps'])):
            # Generate a string with the date of the value in the format %Y-%m-%d
            date_key = date_helpers.datetime_to_str(result['Timestamps'][-i - 1])
            metrics[account_id][metric_name][date_key] = result['Values'][-i - 1]

    return _weight_scores(metrics)


_fetch_accounts()
