#!/usr/bin/env python3

"""Module containing smart contract bug classification according to
Smartbench
"""


# Standard Library
from enum import Enum


class SmartbenchKind(Enum):
    """Class representing bug kind in Smartbench Classification."""

    ACCESS_CONTROL = "Access Control"

    REENTRANCY = "Reentrancy"

    ARITHMETIC = "Arithmetic"

    ADDRESS_VALIDATION = "Address Validation"

    def __str__(self) -> str:
        return self.value

    @staticmethod
    def elements():
        """Return all elements of Smartbench Classification"""
        return [c.value for c in SmartbenchKind]
