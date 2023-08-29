import os


def is_aws_env() -> bool:
    return 'AWS_LAMBDA_FUNCTION_NAME' in os.environ or 'AWS_EXECUTION_ENV' in os.environ


if is_aws_env():
    from helpers import *
    from constants import *
else:
    from assets.lambda_layer.python.helpers import *
    from assets.lambda_layer.python.constants import *
