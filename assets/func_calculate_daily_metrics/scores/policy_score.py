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
# Summary: this module measures whether a customer is leveraging Predictive scaling, Target Tracking (Score of 2), or Simple/Step scaling policies. This is measured based on the NIH driven through each of these policy types.


SP_TYPE_PREDICTIVE = 'PredictiveScaling'
SP_TYPE_TARGET_TRACKING = 'TargetTrackingScaling'
SP_TYPE_SIMPLE = 'SimpleScaling'
SP_TYPE_STEP = 'StepScaling'


def calculate(instance_data: dict, asg_data: dict):
    """
    Calculates the Scaling Policy score.

    :param instance_data: structure with fetched information about Instances in the time window being evaluated
    :param asg_data: structure with fetched information about ASGs in the time window being evaluated

    :return: numeric value of the Scaling Policy Score
    """

    asg_driven_launches = 0
    score = 0

    for _, instance in instance_data.items():
        # The Instance was launched in an ASG
        if instance.asg_name is not None:
            # Check if we could fetch the Instance's ASG data from CloudTrail
            if instance.asg_name in asg_data and asg_data[instance.asg_name].sp is not None:
                asg_driven_launches += 1
                asg = asg_data[instance.asg_name]

                if asg.sp == SP_TYPE_PREDICTIVE:
                    score += 3
                elif asg.sp == SP_TYPE_TARGET_TRACKING:
                    score += 2
                elif asg.sp == SP_TYPE_SIMPLE or asg.sp == SP_TYPE_STEP:
                    score += 1

    # Average the score across all Instances launched in ASGs
    score /= max(1, asg_driven_launches)

    # Scale the score to 10
    return score * 10 / 3
