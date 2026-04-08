#!/usr/bin/env python3
"""
sleep_until — Sleep until a specified time.

Usage:
    sleep_until <time spec>

Supported formats:
    HH:MM           — today at HH:MM (24-hour)
    HH:MM:SS        — today at HH:MM:SS
    +Ns             — sleep N seconds
    +Nm             — sleep N minutes
    +Nh             — sleep N hours
    YYYY-MM-DD HH:MM:SS  — absolute date/time
    YYYY-MM-DDTHH:MM:SS  — ISO 8601 format

Options:
    --verbose       — show target and countdown every second
    -h, --help      — show this help

Exit codes:
    0  — completed normally
    1  — interrupted (Ctrl+C)
    2  — invalid time specification
"""

import argparse
import datetime
import os
import signal
import sys
import time


class Interrupted(Exception):
    """Raised on SIGINT."""
    pass


def parse_relative(spec: str) -> datetime.timedelta | None:
    """Parse +Nh / +Nm / +Ns relative offset. Returns None if not relative."""
    if not spec.startswith("+"):
        return None
    try:
        if spec.endswith("h"):
            return datetime.timedelta(hours=float(spec[1:-1]))
        elif spec.endswith("m"):
            return datetime.timedelta(minutes=float(spec[1:-1]))
        elif spec.endswith("s"):
            return datetime.timedelta(seconds=float(spec[1:-1]))
        else:
            # bare number = seconds
            return datetime.timedelta(seconds=float(spec[1:]))
    except ValueError:
        return None


def parse_absolute(spec: str) -> datetime.datetime | None:
    """Try ISO 8601 / space-separated absolute time formats."""
    fmts = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
    ]
    for fmt in fmts:
        try:
            return datetime.datetime.strptime(spec.strip(), fmt)
        except ValueError:
            pass
    return None


def parse_today(spec: str) -> datetime.datetime | None:
    """Parse HH:MM or HH:MM:SS as today."""
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            t = datetime.datetime.strptime(spec.strip(), fmt).time()
            now = datetime.datetime.now()
            target = datetime.datetime.combine(now.date(), t)
            # If time has passed today, it's tomorrow
            if target <= now:
                target += datetime.timedelta(days=1)
            return target
        except ValueError:
            pass
    return None


def resolve_target(spec: str) -> datetime.datetime:
    """Resolve a time spec string to an absolute datetime."""
    spec = spec.strip()

    # Relative
    rel = parse_relative(spec)
    if rel is not None:
        return datetime.datetime.now() + rel

    # Absolute
    abs_ = parse_absolute(spec)
    if abs_ is not None:
        return abs_

    # Today
    today = parse_today(spec)
    if today is not None:
        return today

    raise ValueError(f"unrecognised time spec: {spec!r}")


def sleep_until(target: datetime.datetime, verbose: bool = False):
    """Block until target datetime. Raises Interrupted on SIGINT."""
    remaining = (target - datetime.datetime.now()).total_seconds()
    if remaining <= 0:
        return

    if verbose:
        print(f"target: {target.isoformat()}  |  sleeping {int(remaining)}s …", flush=True)

    while True:
        now = datetime.datetime.now()
        remaining = (target - now).total_seconds()
        if remaining <= 0:
            break
        if verbose:
            print(f"\r  {int(remaining)}s remaining  ", end="", flush=True)
        # Sleep in 1-second chunks so we respond to SIGINT promptly
        time.sleep(min(1.0, remaining))

    if verbose:
        print()  # newline after countdown


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="sleep_until",
        description="Sleep until a specified time.",
    )
    parser.add_argument("time_spec", nargs="?", help="Time specification")
    parser.add_argument("--verbose", action="store_true")
    args, unknown = parser.parse_known_args(argv)

    if not args.time_spec or unknown:
        parser.print_help()
        return 2

    try:
        target = resolve_target(args.time_spec)
    except ValueError as e:
        print(f"sleep_until: {e}", file=sys.stderr)
        return 2

    # Print target for non-verbose so caller knows when we'll wake
    if not args.verbose:
        print(f"sleeping until {target.isoformat()} ({int((target - datetime.datetime.now()).total_seconds())}s)")

    # Install SIGINT handler
    def sigint_handler(signum, frame):
        print("\nsleep_until: interrupted", file=sys.stderr)
        raise Interrupted()

    old_handler = signal.signal(signal.SIGINT, sigint_handler)

    try:
        sleep_until(target, verbose=args.verbose)
    except Interrupted:
        return 1

    finally:
        signal.signal(signal.SIGINT, old_handler)

    return 0


if __name__ == "__main__":
    sys.exit(main())
