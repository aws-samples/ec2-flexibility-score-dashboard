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
# Summary: Function that implements the backend of a CloudWatch custom widget

import json

from string import Template
from datetime import datetime, timedelta
from libs_finder import *

ACCOUNT_LINE_FORMAT = '$id | $vcpuh | $FlexibilityScore | $InstanceDiversificationScore | $LaunchTemplateScore | $PolicyScore | $ScalingScore'


def generate_markdown(metrics: dict) -> str:
    with open('templates/template.md') as fd:
        md = fd.read()

    template = Template(md)

    if not metrics:
        return template.substitute(
            accounts='*No data*'
        )
    else:
        line_template = Template(ACCOUNT_LINE_FORMAT)

        return template.substitute(
            accounts='\n'.join([
                line_template.substitute(id=a_id, **account_metrics)
                for a_id, account_metrics in metrics.items()
            ])
        )


def handler(event, context):
    time_range = event['widgetContext']['timeRange']

    # Get the scores
    scores = account_manager.fetch_scores(start_time=time_range['start'] // 1000,
                                          end_time=time_range['end'] // 1000)

    # Generate the markdown
    markdown = generate_markdown(scores)

    # Return the HTML minified
    return {"markdown": markdown}


if __name__ == '__main__':
    """
    Convenience method to test the function outside the AWS cloud
    """

    with open('test.json') as fd:
        test_event = json.loads(fd.read())
        test_event['widgetContext']['timeRange']['start'] = (datetime.now() - timedelta(1)).timestamp() * 1000
        test_event['widgetContext']['timeRange']['end'] = datetime.now().timestamp() * 1000
        response = handler(test_event, None)
        print(response)
