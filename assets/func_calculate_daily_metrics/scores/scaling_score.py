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
# Summary: this module is calculated as the ratio of Max Running Instances to the Minimum running instances on any day.


def calculate(instances: dict):
    """
    Calculates the scaling score.

    To identify overlapping running instances, generates a sorted list with all start times and end times.
    Then the list is traversed and a counter is increased when finding a start time,
    and decreased when finding an end time.

    :param instances: structure with fetched information about Instances

    :return: numeric value of the Scaling Score
    """

    min_i = None                # Minimum concurrent running Instances
    max_i = 0                   # Maximum concurrent running Instances
    count = 0                   # Variable to help with concurrency calculations
    prev_start_time = None      # Variable to store the last evaluated start time

    # Flatten running windows of all Instances and sort by time
    windows = [(window.start_time, 'start') for _, instance in instances.items() for window in instance.running_windows]
    windows += [(window.end_time, 'end') for _, instance in instances.items() for window in instance.running_windows
                if window.end_time is not None]
    windows = sorted(windows, key=lambda w: w[0])

    for window in windows:
        # Increment the minimum number of running Instances if more than one consecutive start times are the same
        if prev_start_time is not None and prev_start_time == window[0] and window[1] == 'start':
            min_i += 1

        # Store the start time for the next iteration
        if window[1] == 'start':
            prev_start_time = window[0]

        count += 1 if window[1] == 'start' else -1
        max_i = max(max_i, count)
        min_i = count if min_i is None else min(count, min_i)

    if min_i is None:
        min_i = 0

    # To prevent division by 0
    min_i = max(min_i, 1)

    # Calculate the ratio and the score
    ratio = max_i / min_i

    if ratio > 1.07:
        score = 4
    elif ratio > 1.05:
        score = 3
    elif ratio > 1.02:
        score = 2
    else:
        score = 1

    # Scale the score to 10
    return score * 10 / 4
