from .libs_finder import *
from . import account_manager

_ROUND_DECIMALS = 2


def fetch_scores(start_time, end_time) -> dict:
    """
    Gets account metrics from CloudWatch and calculates the weighted component scores and Flexibility Score

    :param start_time: start of the time window to calculate the scores
    :param end_time: end of the time window to calculate the scores

    :return: dictionary containing the scores

    """

    # Get the weighted metrics for all the accounts in the organization
    account_scores = account_manager.fetch_scores(start_time, end_time)

    return calculate_scores(account_scores)


def calculate_scores(metrics: dict) -> dict:
    """
    Calculates the weighted component scores and Flexibility Score at the organization level
    using fetched account metrics

    :param metrics: weighted metrics of all the accounts

    :return: dictionary containing the organization scores

    """

    # Accumulate the account's vCPU hours
    total_vcpu_h = sum([metrics[CW_METRIC_NAME_VCPU_H] for _, metrics in metrics.items()])

    # Calculate the weighted component scores
    scores = {
        score: round(sum([
            metrics[a_id][score] * metrics[a_id][CW_METRIC_NAME_VCPU_H]
            for a_id in metrics if score in metrics[a_id]
        ]) / total_vcpu_h, _ROUND_DECIMALS) if total_vcpu_h != 0 else 0

        for score in ALL_SCORES
    }

    # Calculate the Flexibility Score
    scores[SCORE_FLEXIBILITY] = round(sum([
        scores[score_name] * score_weight
        for score_name, score_weight in ALL_SCORES.items() if score_name in scores
    ]), _ROUND_DECIMALS)

    return scores
