#!/usr/bin/env python3

import cdk_nag

from aws_cdk import (
    Aspects, App
)
from cdk import MainStack

app = App()
MainStack(app, "FlexibilityScoreStack")

# Check for best practices
Aspects.of(app).add(cdk_nag.AwsSolutionsChecks())

app.synth()
