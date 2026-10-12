"""Reliability metrics that operate on per-image predictions and confidence."""

from collections.abc import Sequence


def flip_rate(original_predictions: Sequence[int], channel_predictions: Sequence[int]) -> float:
    """Return the fraction of predictions changed by a channel."""
    _check_same_length(original_predictions, channel_predictions)
    if not original_predictions:
        return 0.0
    return sum(a != b for a, b in zip(original_predictions, channel_predictions)) / len(original_predictions)


def confident_error_rate(confidence: Sequence[float], correct: Sequence[bool], threshold: float = 0.9) -> float:
    """Return the fraction of all samples that are both confident and wrong."""
    _check_same_length(confidence, correct)
    if not confidence:
        return 0.0
    return sum(score >= threshold and not is_correct for score, is_correct in zip(confidence, correct)) / len(confidence)


def expected_calibration_error(confidence: Sequence[float], correct: Sequence[bool], bins: int = 15) -> float:
    """Calculate equal-width expected calibration error."""
    _check_same_length(confidence, correct)
    if bins < 1:
        raise ValueError("bins must be at least 1")
    if not confidence:
        return 0.0

    total = 0.0
    for index in range(bins):
        lower = index / bins
        upper = (index + 1) / bins
        members = [
            (score, is_correct)
            for score, is_correct in zip(confidence, correct)
            if (score > lower or index == 0) and score <= upper
        ]
        if members:
            accuracy = sum(is_correct for _, is_correct in members) / len(members)
            mean_confidence = sum(score for score, _ in members) / len(members)
            total += len(members) / len(confidence) * abs(accuracy - mean_confidence)
    return total


def _check_same_length(left: Sequence[object], right: Sequence[object]) -> None:
    if len(left) != len(right):
        raise ValueError("metric inputs must have the same length")
