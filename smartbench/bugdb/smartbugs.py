#!/usr/bin/env python3

"""Module containing smart contract bug classification according to
SmartBug curated database: <https://github.com/smartbugs/smartbugs-curated>
"""


# Standard Library
from enum import Enum


class SmartBugsKind(Enum):
    """Class representing bug kind in SmartBugs classification."""

    ACCESS_CONTROL = "Access Control"
    ARITHMETIC = "Arithmetic"
    BAD_RANDOMNESS = "Bad Randomness"
    DENIAL_OF_SERVICE = "Denial Of Service"
    FRONT_RUNNING = "Front Running"
    REENTRANCY = "Reentrancy"
    SHORT_ADDRESSES = "Short Addresses"
    TIME_MANIPULATION = "Time Manipulation"
    UNCHECKED_LOW_LEVEL_CALLS = "Unchecked Low Level Calls"
