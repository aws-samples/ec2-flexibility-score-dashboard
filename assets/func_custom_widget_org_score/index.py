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

from datetime import datetime, timedelta
from string import Template
from libs_finder import *

GAUGE_COLORS = {
    'green': '#31d90f',
    'yellow': '#fae505',
    'orange': '#fa9c05',
    'red': '#fa0505',
    'theme': {
        'light': {
            'gaugeBackground': '#ddd',
            'gaugeInner': '#fff',
            'textColor': '#000'
        },
        'dark': {
            'gaugeBackground': '#ddd',
            'gaugeInner': '#000',
            'textColor': '#fff'
        }
    }
}


def get_colors_by_theme_and_score(theme: str, score) -> dict:
    theme_colors = GAUGE_COLORS['theme'][theme]

    if score is None:
        fill_color = theme_colors['textColor']
    elif score < 3:
        fill_color = GAUGE_COLORS['red']
    elif score < 5:
        fill_color = GAUGE_COLORS['orange']
    elif score < 7:
        fill_color = GAUGE_COLORS['yellow']
    else:
        fill_color = GAUGE_COLORS['green']

    theme_colors['gaugeFill'] = fill_color

    return theme_colors


def generate_gauge_html(colors: dict, score) -> str:
    with open('htm_templates/gauge.html') as fd:
        html = fd.read()

    template = Template(html)

    if score is None:
        gauge_fill_deg = 0
    else:
        gauge_fill_deg = score * 20 if score < 1 else 180 / (10 / score)

    if score is None:
        score = '--'

    return template.substitute(
        gaugeBackground=colors['gaugeBackground'],
        gaugeInner=colors['gaugeInner'],
        gaugeFill=colors['gaugeFill'],
        textColor=colors['textColor'],
        score=score,
        deg=f'{gauge_fill_deg}deg',
        min=0,
        max=10
    )


def generate_large_score_html(colors: dict, score) -> str:
    with open('htm_templates/large_score.html') as fd:
        html = fd.read()

    template = Template(html)

    if score is None:
        score = EMPTY_VALUE

    return template.substitute(
        textColor=colors['gaugeFill'],
        score=score
    )


def extract_score_name_param(widgetContext: dict) -> str:
    try:
        return widgetContext['params']['scoreName']
    except KeyError:
        return SCORE_FLEXIBILITY


def handler(event, context):
    time_range = event['widgetContext']['timeRange']

    # Extract the name of the score to fetch
    score_name = extract_score_name_param(event['widgetContext'])

    # Fetch the score
    score = org_manager.fetch_scores(start_time=time_range['start'] // 1000,
                                     end_time=time_range['end'] // 1000)[score_name]

    # Configure the colors of the chart
    colors = get_colors_by_theme_and_score(event['widgetContext']['theme'], score)

    # Generate the HTML
    html = generate_large_score_html(colors, score) if score_name == SCORE_FLEXIBILITY else \
        generate_gauge_html(colors, score)

    # Return the HTML minified
    return html.replace('\n', '')


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
