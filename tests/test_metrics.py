import pytest

from channel_study.metrics import expected_calibration_error, flip_rate, confident_error_rate


def test_flip_rate_counts_changed_decisions():
    assert flip_rate([0, 1, 1, 2], [0, 2, 1, 0]) == pytest.approx(0.5)


def test_confident_error_rate_uses_all_samples_as_denominator():
    assert confident_error_rate([0.95, 0.91, 0.80, 0.99], [True, False, False, True]) == pytest.approx(0.25)


def test_expected_calibration_error_is_zero_for_perfectly_calibrated_bins():
    assert expected_calibration_error([0.25, 0.75], [False, True], bins=2) == pytest.approx(0.25)


def test_metrics_reject_mismatched_inputs():
    with pytest.raises(ValueError):
        flip_rate([0], [0, 1])
