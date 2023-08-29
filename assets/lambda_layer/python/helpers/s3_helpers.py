import boto3


def upload_file_contents(bucket: str, key: str, contents: str) -> dict:
    """
    Uploads a file to S3 with the contents received as an argument

    :param bucket: S3 bucket to upload the file to
    :param key: full path in the bucket where to upload the file
    :param contents: body of the file to upload

    :return: operation response
    """

    client = boto3.client('s3')
    return client.put_object(Bucket=bucket, Key=key, Body=contents.encode('utf-8'))


def retrieve_file_contents(bucket: str, key: str) -> str:
    """
    Gets a file from S3 and reads all its contents

    :param bucket: S3 bucket to get the file from
    :param key: full path in the bucket of the file to download

    :return: string with all the contents of the file
    """

    client = boto3.client('s3')
    response = client.get_object(Bucket=bucket, Key=key)

    return response['Body'].read().decode('utf-8')
