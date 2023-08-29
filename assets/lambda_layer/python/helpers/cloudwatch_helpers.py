import boto3


def put_metric_data(namespace: str, data: [dict]) -> dict:
    client = boto3.client('cloudwatch')
    return client.put_metric_data(Namespace=namespace, MetricData=data)


def get_metric_data(start_time, end_time, queries) -> dict:
    params = {
        'MetricDataQueries': queries,
        'StartTime': start_time,
        'EndTime': end_time,
        'ScanBy': 'TimestampDescending'
    }

    client = boto3.client('cloudwatch')
    return client.get_metric_data(**params)
