import boto3


def describe_regions(account_id, credentials=None) -> [str]:
    print(f'({account_id}) getting the list of enabled regions...')

    if credentials is None:
        credentials = {}

    client = boto3.client('ec2', **credentials)
    response = client.describe_regions(AllRegions=False)['Regions']

    return [region['RegionName'] for region in response]
