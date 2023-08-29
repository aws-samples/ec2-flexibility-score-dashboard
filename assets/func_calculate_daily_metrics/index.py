#!/usr/bin/env python3

### Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
### SPDX-License-Identifier: MIT-0
###
### Permission is hereby granted, free of charge, to any person obtaining a copy of this
### software and associated documentation files (the "Software"), to deal in the Software
### without restriction, including without limitation the rights to use, copy, modify,
### merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
### permit persons to whom the Software is furnished to do so.
###
### THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
### INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
### PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
### HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
### OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
### SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Author: Borja Pérez Guasch <bpguasch@amazon.com>
# Summary: calculates the Flexibility Score using 4 components: Scaling Score, Launch Template Score, Scaling Policy Score and Instance Diversification Score. This index handler retrieves data that the modules need to calculate the scores.

import json

from datetime import datetime, timedelta
from scores import *
from libs_finder import *


def generate_time_window_for_fetching_data(beforehand_days: int = 1) -> TimeWindow:
    """
    Generates a time window that is used to retrieve CloudTrail events.
    By default, the time window is the day before the time of execution.

    :return: TimeWindow object with a start time and end time
    """

    target_day = datetime.now() - timedelta(beforehand_days)

    start_time = datetime(target_day.year, target_day.month, target_day.day, 0, 0, 0, tzinfo=date_helpers.get_timezone())
    end_time = datetime(target_day.year, target_day.month, target_day.day, 23, 59, 59, tzinfo=date_helpers.get_timezone())

    return TimeWindow(start_time, end_time)


def publish_metrics_in_cloudwatch(metrics_by_account: dict) -> None:
    metric_data = [
        {
            'MetricName': name,
            'Value': value,
            'Unit': 'None',
            'Timestamp': datetime.now(),
            'Dimensions': [
                {
                    'Name': CW_DIMENSION_NAME_ACCOUNT_ID,
                    'Value': account_id
                },
            ],
        }
        for account_id, metrics in metrics_by_account.items() for name, value in metrics.items()
    ]

    print('Publishing metrics to CloudWatch...', end=' ')

    cloudwatch_helpers.put_metric_data(CW_NAMESPACE, metric_data)

    print('done!')


def upload_metrics_to_s3(metrics_by_account: dict) -> None:
    folder = date_helpers.datetime_to_str(datetime_format='%Y/%m/%d')
    file_name = date_helpers.datetime_to_str(datetime_format='%H%M%S')
    bucket = os.environ['BUCKET']

    print('Uploading metrics to S3...', end=' ')

    s3_helpers.upload_file_contents(bucket, f'{folder}/{file_name}.json', json.dumps(metrics_by_account))

    print('done!')


def calculate_daily_metrics() -> dict:
    """
    Calculates daily account and organization metrics

    :return: dictionary containing the metrics
    """

    metrics = {
        a_id: {
            CW_METRIC_NAME_VCPU_H: account.vcpu_h,
            SCORE_LT: launch_template_score.calculate(account.instances),
            SCORE_POLICY: policy_score.calculate(account.instances, account.asg),
            SCORE_DIVERSIFICATION: instance_diversification_score.calculate(account.asg, account.lt),
            SCORE_SCALING: scaling_score.calculate(account.instances)
        }

        for a_id, account in account_manager.accounts.items()
    }

    metrics.update({
        CW_DIMENSION_VALUE_ORG: org_manager.calculate_scores(metrics)
    })

    return metrics


def handler(event, context):
    # Build a time window (yesterday throughout the day) for calculating metrics
    tw = generate_time_window_for_fetching_data()

    # Fetch the organization's accounts and their resources
    account_manager.fetch_resources(tw)

    # Calculate account metrics
    metrics = calculate_daily_metrics()

    print('Calculated metrics', metrics)

    # Publish metrics in CloudWatch and upload them to S3
    publish_metrics_in_cloudwatch(metrics)
    upload_metrics_to_s3(metrics)


if __name__ == '__main__':
    """
    Convenience method to test the function outside of the AWS cloud
    """

    handler({}, None)
