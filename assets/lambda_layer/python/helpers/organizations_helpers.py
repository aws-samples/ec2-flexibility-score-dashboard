import boto3


def describe_organization() -> dict:
    client = boto3.client('organizations')
    return client.describe_organization()['Organization']


def list_organization_accounts() -> [dict]:
    client = boto3.client('organizations')
    paginator = client.get_paginator('list_accounts')
    return list(paginator.paginate().search('Accounts[]'))
