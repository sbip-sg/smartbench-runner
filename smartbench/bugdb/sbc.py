#!/usr/bin/env python3

"""Module containing smart contract bug classification according to
SmartBug Curated database: <https://github.com/smartbugs/smartbugs-curated>
"""


# Standard Library
from enum import Enum
from typing import List


class SmartBugsPP(Enum):
    """Class representing bug kind in SmartBugs++ Classification."""

    ACCESS_CONTROL = "Access Control"
    ASSERTION_FAILURE = "Assertion Failure"
    ARITHMETIC = "Arithmetic"
    BAD_RANDOMNESS = "Bad Randomness"
    DENIAL_OF_SERVICE = "Denial Of Service"
    FRONT_RUNNING = "Front Running"
    LEAKING_ETHER = "Leaking Ether"
    LOCKING_ETHER = "Locking Ether"
    REENTRANCY = "Reentrancy"
    SHORT_ADDRESSES = "Short Addresses"
    TIME_MANIPULATION = "Time Manipulation"
    TRANSACTION_ORDER_DEPENDENCY = "Transaction Order Dependency"
    UNCHECKED_LOW_LEVEL_CALLS = "Unchecked Low Level Calls"
    UNHANDLED_EXCEPTION = "Unhandled Exception"
    UNPROTECTED_SELFDESTRUCT = "Unprotected Selfdestruct"
    UNSAFE_DELEGATECALL = "Unsafe Delegatecall"

    @staticmethod
    def elements():
        """Return all elements of SmartBugs Classification"""
        return [c.value for c in SmartBugsPP]
