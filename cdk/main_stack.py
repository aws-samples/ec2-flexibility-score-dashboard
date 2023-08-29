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
# Summary: main application Stack

from aws_cdk import (
    Stack, CfnParameter
)
from constructs import Construct
from .modules import *


class MainStack(Stack):
    def _create_param_org_role_name(self) -> CfnParameter:
        return CfnParameter(self, 'ParamOrgRoleName', default='OrganizationAccountAccessRole')

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a parameter to hold the organizations role name
        org_role_name = self._create_param_org_role_name()

        # Create an S3 bucket to store metrics calculations
        buckets = S3Module.create(self)

        # Create the Lambda functions
        funcs = LambdaModule.create(self, buckets, org_role_name)

        # Create the CloudWatch dashboard
        CloudWatchModule.create(self, funcs)
