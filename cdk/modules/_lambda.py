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
# Summary: module that deploys AWS Lambda related resources

from aws_cdk import (
    aws_lambda as _lambda,
    RemovalPolicy,
    Duration,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as event_targets,
    Stack,
    custom_resources
)
from constructs import Construct
from assets.lambda_layer.python.constants import *
from cdk_nag import NagSuppressions, NagPackSuppression


class LambdaModule:
    context: Construct

    @classmethod
    def _create_layer(cls) -> _lambda.LayerVersion:
        return _lambda.LayerVersion(
            cls.context,
            'LambdaLayer',
            code=_lambda.Code.from_asset('assets/lambda_layer'),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_10],
            removal_policy=RemovalPolicy.DESTROY,
            layer_version_name='FlexibilityScoreHelpers'
        )

    @classmethod
    def _create_func_daily_metrics_calculation(cls, layer, bucket, org_role_name) -> None:
        func = _lambda.Function(
            cls.context,
            'FuncDailyMetricsCalculation',
            function_name='calculateDailyMetrics',
            timeout=Duration.minutes(15),
            runtime=_lambda.Runtime.PYTHON_3_10,
            environment={
                'BUCKET': bucket.bucket_name,
                'ORGS_IAM_ROLE': org_role_name.value_as_string
            },
            code=_lambda.Code.from_asset('assets/func_calculate_daily_metrics'),
            handler='index.handler',
            layers=[layer],
            memory_size=256
        )

        # Grant the function permission to write to the S3 Bucket
        bucket.grant_write(func)

        # Define a structure containing the permissions needed by the function
        statements = [
            {
                'actions': [
                    "organizations:ListAccounts",
                    "organizations:DescribeOrganization",
                    "cloudtrail:LookupEvents",
                    "ec2:DescribeRegions",
                    "cloudwatch:PutMetricData"

                ],
                'resources': ['*']
            },
            {
                'actions': ['sts:AssumeRole'],
                'resources': [f'arn:aws:iam::*:role/{org_role_name.value_as_string}']
            }
        ]

        # Attach the permissions to the function execution role
        for statement in statements:
            func.add_to_role_policy(iam.PolicyStatement(
                actions=statement['actions'],
                resources=statement['resources'],
                effect=iam.Effect.ALLOW
            ))

        # The alias will be used to trigger the function using an EventBridge Rule
        alias = _lambda.Alias(
            cls.context,
            'FuncAliasDailyMetricsCalculation',
            alias_name='Prod',
            version=func.current_version
        )

        # Create a rule that executes the prod alias every 3 hours
        events.Rule(
            cls.context,
            'DailyMetricsCalculationRule',
            schedule=events.Schedule.rate(Duration.hours(3)),
            targets=[event_targets.LambdaFunction(alias)]
        )

        # Execute the function manually once when deploying the stack
        custom_resources.AwsCustomResource(
            cls.context, 'ExecuteFuncCustomResource',
            on_create=custom_resources.AwsSdkCall(
                service='Lambda',
                action='invoke',
                physical_resource_id=custom_resources.PhysicalResourceId.of(alias.alias_name),
                parameters={
                    'InvocationType': 'Event',
                    'FunctionName': alias.function_name
                }
            ),
            removal_policy=RemovalPolicy.DESTROY,
            function_name='dailyMetricsCalculationOneOffExecution',
            policy=custom_resources.AwsCustomResourcePolicy.from_statements(
                [
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=['lambda:InvokeFunction'],
                        resources=[alias.function_arn]
                    )
                ]
            )
        )

        NagSuppressions.add_resource_suppressions(func, [NagPackSuppression(
            id='AwsSolutions-IAM5',
            reason='Wildcard is needed since individual ids are not available at deploy time.'
        )], True)

        NagSuppressions.add_resource_suppressions(func, [NagPackSuppression(
            id='AwsSolutions-IAM4',
            reason='Managed policy needed to specify permissions over other resources.'
        )], True)

    @classmethod
    def _create_func_custom_widget_org_score(cls, layer) -> _lambda.Alias:
        func = _lambda.Function(
            cls.context,
            'FuncCustomWidgetOrgScore',
            function_name='customWidgetOrgScore',
            timeout=Duration.minutes(1),
            runtime=_lambda.Runtime.PYTHON_3_10,
            code=_lambda.Code.from_asset('assets/func_custom_widget_org_score'),
            handler='index.handler',
            layers=[layer],
            reserved_concurrent_executions=5
        )

        func.add_to_role_policy(iam.PolicyStatement(
            actions=["cloudwatch:GetMetricData", "organizations:ListAccounts", "organizations:DescribeOrganization"],
            resources=['*'],
            effect=iam.Effect.ALLOW
        ))

        NagSuppressions.add_resource_suppressions(func, [NagPackSuppression(
            id='AwsSolutions-IAM5',
            reason='Wildcard is needed since individual ids are not available at deploy time.'
        )], True)

        NagSuppressions.add_resource_suppressions(func, [NagPackSuppression(
            id='AwsSolutions-IAM4',
            reason='Managed policy needed to specify permissions over other resources.'
        )], True)

        # The alias will be used to render the CloudWatch widget
        return _lambda.Alias(
            cls.context,
            'FuncAliasCustomWidgetOrgScore',
            alias_name='Prod',
            version=func.current_version
        )

    @classmethod
    def _create_func_custom_widget_account_rank(cls, layer) -> _lambda.Alias:
        func = _lambda.Function(
            cls.context,
            'FuncCustomWidgetAccountRank',
            function_name='customWidgetAccountRank',
            timeout=Duration.minutes(1),
            runtime=_lambda.Runtime.PYTHON_3_10,
            code=_lambda.Code.from_asset('assets/func_custom_widget_account_rank'),
            handler='index.handler',
            layers=[layer],
            reserved_concurrent_executions=5
        )

        func.add_to_role_policy(iam.PolicyStatement(
            actions=["cloudwatch:GetMetricData", "organizations:ListAccounts", "organizations:DescribeOrganization"],
            resources=['*'],
            effect=iam.Effect.ALLOW
        ))

        NagSuppressions.add_resource_suppressions(func, [NagPackSuppression(
            id='AwsSolutions-IAM5',
            reason='Wildcard is needed since individual ids are not available at deploy time.'
        )], True)

        NagSuppressions.add_resource_suppressions(func, [NagPackSuppression(
            id='AwsSolutions-IAM4',
            reason='Managed policy needed to specify permissions over other resources.'
        )], True)

        # The alias will be used to render the CloudWatch widget
        return _lambda.Alias(
            cls.context,
            'FuncAliasCustomWidgetAccountRank',
            alias_name='Prod',
            version=func.current_version
        )

    @classmethod
    def _create_func_custom_widget_accounts_scores(cls, layer) -> _lambda.Alias:
        func = _lambda.Function(
            cls.context,
            'FuncCustomWidgetAccountsScores',
            function_name='customWidgetAccountsScores',
            timeout=Duration.minutes(1),
            runtime=_lambda.Runtime.PYTHON_3_10,
            code=_lambda.Code.from_asset('assets/func_custom_widget_accounts_scores'),
            handler='index.handler',
            layers=[layer],
            reserved_concurrent_executions=5
        )

        func.add_to_role_policy(iam.PolicyStatement(
            actions=["cloudwatch:GetMetricData", "organizations:ListAccounts", "organizations:DescribeOrganization"],
            resources=['*'],
            effect=iam.Effect.ALLOW
        ))

        NagSuppressions.add_resource_suppressions(func, [NagPackSuppression(
            id='AwsSolutions-IAM5',
            reason='Wildcard is needed since individual ids are not available at deploy time.'
        )], True)

        NagSuppressions.add_resource_suppressions(func, [NagPackSuppression(
            id='AwsSolutions-IAM4',
            reason='Managed policy needed to specify permissions over other resources.'
        )], True)

        # The alias will be used to render the CloudWatch widget
        return _lambda.Alias(
            cls.context,
            'FuncAliasCustomWidgetAccountsScores',
            alias_name='Prod',
            version=func.current_version
        )

    @classmethod
    def create(cls, context: Construct, buckets, org_role_name) -> dict:
        NagSuppressions.add_stack_suppressions(
            stack=Stack.of(context),
            suppressions=[
                NagPackSuppression(
                    id='AwsSolutions-L1',
                    reason='Deploying Lambda functions with the latest runtime is not a requirement.'
                ),
                NagPackSuppression(
                    id='AwsSolutions-IAM4',
                    reason='Needed to execute an SDK call.'
                )
            ]
        )

        cls.context = context

        layer = cls._create_layer()
        cls._create_func_daily_metrics_calculation(layer, buckets[BUCKET_METRICS], org_role_name)

        return {
            FUNC_ORG_SCORE: cls._create_func_custom_widget_org_score(layer),
            FUNC_ACCOUNTS_SCORES: cls._create_func_custom_widget_accounts_scores(layer),
            FUNC_ACCOUNT_RANK: cls._create_func_custom_widget_account_rank(layer)
        }
