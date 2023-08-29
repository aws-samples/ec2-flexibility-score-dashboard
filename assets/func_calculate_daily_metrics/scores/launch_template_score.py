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
# Summary: this module is calculated as the ratio of normalized instance hours (NIH) driven by Launch Templates to NIH driven through Launch Configuration based Autoscaling groups.


def calculate(instances: dict):
    """
    Calculates the Launch Template score.

    :param instances: structure with fetched information about Instances

    :return: numeric value of the Launch Template Score
    """

    lt_vcpu_h = 0
    lc_vcpu_h = 0

    for _, instance in instances.items():
        # Launched in an ASG driven by a Launch Template
        if instance.asg_name is not None and instance.lt is not None:
            lt_vcpu_h += instance.vcpu_h
        # Launched in an ASG driven by a Launch Configuration
        elif instance.asg_name is not None and instance.lt_name is None:
            lc_vcpu_h += instance.vcpu_h

    return 0 if lt_vcpu_h == lc_vcpu_h == 0 else (lt_vcpu_h / (lt_vcpu_h + lc_vcpu_h)) * 10
