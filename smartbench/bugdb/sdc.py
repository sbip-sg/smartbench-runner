#!/usr/bin/env python3

"""Module containing smart contract bug classification according to
SolidiFI: <https://github.com/DependableSystemsLab/SolidiFI>
"""


# Standard Library
from enum import Enum


class SolidiFIPP(Enum):
    """Class representing bug kind in SolidiFI Classification."""

    OVERFLOW_UNDERFLOW = "Overflow/Underflow"

    REENTRANCY = "Reentrancy"

    TOD = "TOD"

    TIMESTAMP_DEPENDENCY = "Timestamp Dependency"

    UNCHECKED_SEND = "Unchecked Send"

    UNHANDLED_EXCEPTION = "Unhandled Exception"

    TX_ORIGIN = "Tx Origin"

    def __str__(self) -> str:
        return self.value

    @staticmethod
    def elements():
        """Return all elements of SolidiFI Classification"""
        return [c.value for c in SolidiFIPP]
