MAX_CT_RELATIVE_DAYS_SEARCH = 90

DEFAULT = '$Default'
EMPTY_VALUE = '--'

# CloudTrail resource types
RESOURCE_TYPE_INSTANCE = 'AWS::EC2::Instance'
RESOURCE_TYPE_LT = 'AWS::EC2::LaunchTemplate'
RESOURCE_TYPE_ASG = 'AWS::AutoScaling::AutoScalingGroup'
RESOURCE_TYPE_SP = 'AWS::AutoScaling::ScalingPolicy'

# EC2 Instance Lifecycle event CloudTrail codes
EVENT_CODE_RUNNING = 16
EVENT_CODE_PENDING = 0

# EC2 Instance market options
MARKET_SPOT = 'spot'

# EC2 Instance CloudTrail event names
EVENT_NAME_BID_EVICTED = 'BidEvictedEvent'
EVENT_NAME_TERMINATE_INSTANCES = 'TerminateInstances'
EVENT_NAME_RUN_INSTANCES = 'RunInstances'
EVENT_NAME_START_INSTANCES = 'StartInstances'
EVENT_NAME_STOP_INSTANCES = 'StopInstances'
ALL_INSTANCE_EVENT_NAMES = {EVENT_NAME_BID_EVICTED, EVENT_NAME_TERMINATE_INSTANCES, EVENT_NAME_RUN_INSTANCES,
                            EVENT_NAME_START_INSTANCES, EVENT_NAME_STOP_INSTANCES}

# Launch Template CloudTrail event names
EVENT_NAME_CREATE_LT = 'CreateLaunchTemplate'
EVENT_NAME_CREATE_LT_VERSION = 'CreateLaunchTemplateVersion'
EVENT_NAME_MODIFY_LT = 'ModifyLaunchTemplate'
ALL_LT_EVENT_NAMES = {EVENT_NAME_CREATE_LT, EVENT_NAME_CREATE_LT_VERSION, EVENT_NAME_MODIFY_LT}

# ASG CloudTrail event names
EVENT_NAME_CREATE_ASG = 'CreateAutoScalingGroup'
EVENT_NAME_DELETE_ASG = 'DeleteAutoScalingGroup'
EVENT_NAME_UPDATE_ASG = 'UpdateAutoScalingGroup'
ALL_ASG_EVENT_NAMES = {EVENT_NAME_CREATE_ASG, EVENT_NAME_DELETE_ASG, EVENT_NAME_UPDATE_ASG}

# Scaling Policy CloudTrail event names
EVENT_NAME_PUT_SP = 'PutScalingPolicy'
EVENT_NAME_DELETE_SP = 'DeletePolicy'
ALL_SP_EVENT_NAMES = {EVENT_NAME_PUT_SP, EVENT_NAME_DELETE_SP}

# Flex score's score component names
SCORE_DIVERSIFICATION = 'InstanceDiversificationScore'
SCORE_LT = 'LaunchTemplateScore'
SCORE_POLICY = 'PolicyScore'
SCORE_SCALING = 'ScalingScore'
SCORE_FLEXIBILITY = 'FlexibilityScore'

ALL_SCORES = {
    SCORE_DIVERSIFICATION: 0.25,
    SCORE_LT: 0.25,
    SCORE_POLICY: 0.15,
    SCORE_SCALING: 0.35
}

INSTANCE_NORMALIZATION_TABLE = {
    'nano': 0.25,
    'micro': 0.5,
    'small': 1,
    'medium': 2,
    'large': 4,
    'xlarge': 8,
    '2xlarge': 16,
    '3xlarge': 24,
    '4xlarge': 32,
    '6xlarge': 48,
    '8xlarge': 64,
    '9xlarge': 72,
    '10xlarge': 80,
    '12xlarge': 96,
    '16xlarge': 128,
    '18xlarge': 144,
    '24xlarge': 192,
    '32xlarge': 256,
    '56xlarge': 448,
    '112xlarge': 896
}

CW_NAMESPACE = 'FlexibilityScore'
CW_DIMENSION_NAME_ACCOUNT_ID = 'accountId'
CW_DIMENSION_VALUE_ORG = 'ORG'
CW_METRIC_NAME_VCPU_H = 'vcpuh'
CW_METRIC_PERIOD = 3600
ALL_CW_METRICS = {SCORE_DIVERSIFICATION, SCORE_LT, SCORE_POLICY, SCORE_SCALING, CW_METRIC_NAME_VCPU_H}

BUCKET_METRICS = 'BUCKET_METRICS'

FUNC_ORG_SCORE = 'FUNC_ORG_SCORE'
FUNC_ACCOUNT_RANK = 'FUNC_ACCOUNT_RANK'
FUNC_ACCOUNTS_SCORES = 'FUNC_ACCOUNTS_SCORES'
