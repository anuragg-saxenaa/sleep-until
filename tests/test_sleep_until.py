"""Tests for sleep_until time-parsing logic."""

import datetime
from sleep_until import parse_relative, parse_absolute, parse_today, resolve_target


class TestParseRelative:
    def test_hours(self):
        assert parse_relative("+2h") == datetime.timedelta(hours=2)

    def test_minutes(self):
        assert parse_relative("+30m") == datetime.timedelta(minutes=30)

    def test_seconds(self):
        assert parse_relative("+45s") == datetime.timedelta(seconds=45)

    def test_bare_seconds(self):
        assert parse_relative("+120") == datetime.timedelta(seconds=120)

    def test_not_relative(self):
        assert parse_relative("14:30") is None

    def test_invalid(self):
        assert parse_relative("+abc") is None


class TestParseAbsolute:
    def test_iso_space(self):
        result = parse_absolute("2026-04-09 09:00:00")
        assert result == datetime.datetime(2026, 4, 9, 9, 0, 0)

    def test_iso_T(self):
        result = parse_absolute("2026-04-09T09:00")
        assert result == datetime.datetime(2026, 4, 9, 9, 0)

    def test_invalid(self):
        assert parse_absolute("hello") is None


class TestParseToday:
    def test_HHMM(self):
        result = parse_today("14:30")
        assert result is not None
        assert result.hour == 14
        assert result.minute == 30

    def test_HHMMSS(self):
        result = parse_today("14:30:45")
        assert result is not None
        assert result.hour == 14
        assert result.minute == 30
        assert result.second == 45

    def test_invalid(self):
        assert parse_today("abc") is None


class TestResolveTarget:
    def test_relative(self):
        target = resolve_target("+5m")
        assert target > datetime.datetime.now()
        diff = (target - datetime.datetime.now()).total_seconds()
        assert 299 < diff < 301

    def test_absolute(self):
        target = resolve_target("2026-04-09 09:00:00")
        assert target == datetime.datetime(2026, 4, 9, 9, 0, 0)

    def test_today(self):
        target = resolve_target("23:59")
        assert target is not None
        assert target.minute == 59
        assert target.hour == 23

    def test_invalid_raises(self):
        import pytest
        with pytest.raises(ValueError):
            resolve_target("not a time")