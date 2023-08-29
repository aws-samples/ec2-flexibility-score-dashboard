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
# Summary: module that deploys S3 related resources

from aws_cdk import (
    RemovalPolicy,
    aws_s3 as s3,
)

from constructs import Construct
from assets.lambda_layer.python.constants import *
from ..utils import *


class S3Module:
    context: Construct

    @classmethod
    def _create_calculation_files_bucket(cls, suffix: str) -> s3.Bucket:
        bucket = s3.Bucket(
            cls.context,
            'CalculationFilesBucket',
            bucket_name=f'flexibility-score-{suffix}',
            removal_policy=RemovalPolicy.DESTROY,
            enforce_ssl=True,
            server_access_logs_prefix='server-access-logs/',
            block_public_access=s3.BlockPublicAccess(
                block_public_policy=True,
                block_public_acls=True,
                restrict_public_buckets=True,
                ignore_public_acls=True
            ),
            auto_delete_objects=True
        )

        return bucket

    @classmethod
    def create(cls, context: Construct) -> dict:
        cls.context = context

        return {
            BUCKET_METRICS: cls._create_calculation_files_bucket(
                suffix=stack_utils.stack_id_termination(
                    context=cls.context
                )
            )
        }
