import pytest

from app_tabs.split_tab import _looks_like_float, parse_timestamp_to_seconds


@pytest.mark.parametrize(
    "value, expected",
    [
        ("90", 90.0),
        ("3.5", 3.5),
        ("01:02", 62.0),
        ("1:02:03", 3723.0),
    ],
)
def test_parse_timestamp_to_seconds(value: str, expected: float) -> None:
    assert parse_timestamp_to_seconds(value) == pytest.approx(expected)


def test_parse_timestamp_to_seconds_invalid_inputs() -> None:
    for bad_input in ["", "abc", "1:2:3:4", "1:xx"]:
        with pytest.raises(ValueError):
            parse_timestamp_to_seconds(bad_input)


@pytest.mark.parametrize(
    "text, expected",
    [("3.14", True), ("-0.5", True), ("abc", False), ("", False)],
)
def test_looks_like_float(text: str, expected: bool) -> None:
    assert _looks_like_float(text) is expected
