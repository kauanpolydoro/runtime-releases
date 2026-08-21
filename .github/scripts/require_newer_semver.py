#!/usr/bin/env python3
"""Reject a candidate that is not newer than the current stable patch release."""

from __future__ import annotations

import re
import sys

SEMVER_PATTERN = re.compile(r"v?(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")
EXPECTED_ARGUMENT_COUNT = 3


def parse_patch_version(value: str) -> tuple[int, int, int]:
    match = SEMVER_PATTERN.fullmatch(value)
    if match is None:
        raise ValueError(f"invalid semantic patch version: {value!r}")
    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch)


def main(argv: list[str]) -> int:
    if len(argv) != EXPECTED_ARGUMENT_COUNT:
        sys.stderr.write("usage: require_newer_semver.py CANDIDATE CURRENT_STABLE\n")
        return 2
    try:
        candidate = parse_patch_version(argv[1])
        current_stable = parse_patch_version(argv[2])
    except ValueError as error:
        sys.stderr.write(f"{error}\n")
        return 2
    if candidate <= current_stable:
        sys.stderr.write(
            f"candidate v{'.'.join(map(str, candidate))} must be newer than "
            f"stable v{'.'.join(map(str, current_stable))}\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
