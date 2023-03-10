#!/usr/bin/env python3

"""Module containing smart contract bug classification according to
SmartBug curated database: <https://github.com/smartbugs/smartbugs-curated>
"""


# Standard Library
from enum import Enum


class SBC(Enum):
    """Class representing SmartBugs Curated Classification for smart
    contract bugs."""

    REENTRANCY = "Reentrancy"
    ACCESS_CONTROL = "Access Control"
    ARITHMETIC = "Arithmetic"
    UNCHECKED_LOW_LEVEL_CALLS = "Unchecked Low Level Calls"
    DENIAL_OF_SERVICE = "Denial Of Service"
    BAD_RANDOMNESS = "Bad Randomness"
    FRONT_RUNNING = "Front Running"
    TIME_MANIPULATION = "Time Manipulation"
    SHORT_ADDRESSES = "Short Addresses"
