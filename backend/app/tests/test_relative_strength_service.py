from app.services.relative_strength_service import (
    calculate_brsi_score,
    calculate_excess_return,
    calculate_return_pct,
    map_brsi_status,
    percentile_ranks,
)


def test_calculate_excess_return() -> None:
    assert calculate_excess_return(8.5, 3.0) == 5.5
    assert calculate_excess_return(None, 3.0) is None
    assert calculate_excess_return(8.5, None) is None


def test_calculate_return_pct() -> None:
    rows = [{"close": 100}, {"close": 105}, {"close": 110}]
    assert calculate_return_pct(rows, 1) == 4.761904761904762
    assert calculate_return_pct(rows, 24) is None


def test_percentile_ranks() -> None:
    ranks = percentile_ranks({"ETH/USDT": 2.0, "SOL/USDT": 8.0, "ADA/USDT": 5.0})
    assert ranks["ETH/USDT"] == 0
    assert ranks["ADA/USDT"] == 50
    assert ranks["SOL/USDT"] == 100


def test_brsi_score_generation() -> None:
    score = calculate_brsi_score(
        {
            "excess_return_24h": 80,
            "excess_return_7d": 70,
            "excess_return_30d": 60,
            "relative_trend_score": 50,
            "volume_score": 40,
        }
    )
    assert score == 66
    partial_score = calculate_brsi_score(
        {
            "excess_return_24h": 80,
            "excess_return_7d": 70,
            "excess_return_30d": None,
            "relative_trend_score": 50,
            "volume_score": None,
        }
    )
    assert partial_score == 71.42857142857143
    assert calculate_brsi_score({"excess_return_24h": None}) is None


def test_status_mapping() -> None:
    assert map_brsi_status(85) == "Very Strong"
    assert map_brsi_status(70) == "Strong"
    assert map_brsi_status(55) == "Slightly Strong"
    assert map_brsi_status(40) == "Slightly Weak"
    assert map_brsi_status(25) == "Weak"
    assert map_brsi_status(10) == "Very Weak"
    assert map_brsi_status(None) == "Insufficient Data"
