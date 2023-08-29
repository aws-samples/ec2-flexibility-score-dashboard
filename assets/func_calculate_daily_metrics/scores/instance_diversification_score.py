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
# Summary: this module measures how well-diversified a Mixed Instance ASG is, to leverage EC2 Spot in the most cost-capacity effective way.


def calculate(asg_data: dict, lt_data: dict):
    """
    Calculates the Instance diversification score.

    :param asg_data: structure with fetched information about ASGs in the time window being evaluated
    :param lt_data: structure with fetched information about Launch Templates in the time window being evaluated

    :return: numeric value of the Instance Diversification Score
    """

    score = 0

    for _, asg in asg_data.items():
        # Launch configuration based ASGs get the min score
        if asg.lt is None:
            score += 1
        # Overrides take precedence so check those first
        elif asg.overrides.uses_abis:
            score += 5
        elif asg.overrides.instance_count is not None:
            if asg.overrides.instance_count > 15:
                score += 5
            elif 11 <= asg.overrides.instance_count <= 15:
                score += 4
            elif 6 <= asg.overrides.instance_count <= 10:
                score += 3
            elif 2 <= asg.overrides.instance_count <= 5:
                score += 2
            else:
                score += 1
        # This means that the ASG uses LT and does not have overrides. Get the score from the LT configuration
        else:
            # Verify that we fetched the data of the LT used by the ASG
            if asg.lt.id in lt_data and asg.lt.version in lt_data[asg.lt.id].versions:
                used_version = lt_data[asg.lt.id].versions[asg.lt.version]

                # If the version of the used LT uses ABS add the max score, otherwise add the min score
                score += 5 if used_version.uses_abis else 1

    # Average the score across all ASGs
    score /= max(1, len(asg_data))

    # Scale the score to 10
    return score * 10 / 5
