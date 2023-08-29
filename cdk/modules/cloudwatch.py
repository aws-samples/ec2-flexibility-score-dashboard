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
# Summary: module that deploys CloudWatch related resources

import re

from aws_cdk import (
    aws_cloudwatch as cloudwatch
)
from constructs import Construct
from assets.lambda_layer.python.constants import *

_MAX_SIZE = 24


def camel_case_split(string) -> str:
    return ' '.join(re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', string))


def read_component_description(score: str) -> str:
    with open(f'assets/dashboard/text/{score}.md') as fd:
        return fd.read()


class CloudWatchModule:
    context: Construct
    funcs: dict

    @classmethod
    def _create_dashboard(cls) -> None:
        # ---------------------------------------- ROW 1 ---------------------------------------- #
        flex_score_widget = cloudwatch.CustomWidget(
            function_arn=cls.funcs[FUNC_ORG_SCORE].function_arn,
            title='Flexibility Score',
            width=5,
            height=6,
            update_on_resize=False,
            params={'scoreName': 'FlexibilityScore'}
        )

        flex_score_text = cloudwatch.TextWidget(
            markdown=read_component_description(SCORE_FLEXIBILITY),
            height=flex_score_widget.height,
            width=_MAX_SIZE - flex_score_widget.width
        )

        row_1 = cloudwatch.Row(flex_score_widget, flex_score_text)

        # ------------------------------------- ROWS 2 TO 3 ------------------------------------- #
        component_widgets = [
            cloudwatch.CustomWidget(
                function_arn=cls.funcs[FUNC_ORG_SCORE].function_arn,
                title=camel_case_split(score),
                width=5,
                height=flex_score_widget.height + 1,
                update_on_resize=False,
                params={'scoreName': score}
            )

            for score in ALL_SCORES
        ]

        component_description_widgets = [
            cloudwatch.TextWidget(
                markdown=read_component_description(score),
                height=component_widgets[0].height,
                width=(_MAX_SIZE - (component_widgets[0].width * 2)) / 2
            )

            for score in ALL_SCORES
        ]

        # ---------------------------------------- ROW 4 ---------------------------------------- #
        account_rank_widget = cloudwatch.CustomWidget(
            function_arn=cls.funcs[FUNC_ACCOUNT_RANK].function_arn,
            title='',
            width=_MAX_SIZE / 3,
            height=10,
            update_on_resize=False,
            params={'count': 3}
        )

        accounts_scores_widget = cloudwatch.CustomWidget(
            function_arn=cls.funcs[FUNC_ACCOUNTS_SCORES].function_arn,
            title='',
            width=_MAX_SIZE - account_rank_widget.width,
            height=account_rank_widget.height,
            update_on_resize=False
        )

        row_4 = cloudwatch.Row(account_rank_widget, accounts_scores_widget)

        # ---------------------------------------- ROW 5 ---------------------------------------- #
        score_trends_widget = cloudwatch.GraphWidget(
            height=account_rank_widget.height,
            width=_MAX_SIZE,
            title='Component scores trend'
        )

        for score in ALL_SCORES:
            score_trends_widget.add_left_metric(
                cloudwatch.Metric(
                    namespace='FlexibilityScore',
                    metric_name=score,
                    dimensions_map={
                        'accountId': 'ORG'
                    }
                )
            )

        # Dashboard
        cloudwatch.Dashboard(
            cls.context,
            'Dashboard',
            dashboard_name='Flexibility-Score-Dashboard',
            period_override=cloudwatch.PeriodOverride.INHERIT,
            start='-D1',
            widgets=[
                row_1.widgets,
                [component_widgets[0], component_description_widgets[0], component_widgets[1], component_description_widgets[1]],
                [component_widgets[2], component_description_widgets[2], component_widgets[3], component_description_widgets[3]],
                row_4.widgets,
                [score_trends_widget]
            ]
        )

    @classmethod
    def create(cls, context: Construct, funcs) -> None:
        cls.context = context
        cls.funcs = funcs

        cls._create_dashboard()
