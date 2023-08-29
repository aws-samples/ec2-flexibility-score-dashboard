import boto3


def get_caller_identity() -> dict:
    client = boto3.client('sts')
    return client.get_caller_identity()


def assume_role(role_arn: str) -> dict:
    client = boto3.client('sts')

    response = client.assume_role(
        RoleArn=role_arn,
        RoleSessionName="RoleAssume"
    )

    return {
        'aws_access_key_id': response["Credentials"]["AccessKeyId"],
        'aws_secret_access_key': response["Credentials"]["SecretAccessKey"],
        'aws_session_token': response["Credentials"]["SessionToken"],
    }
