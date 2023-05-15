#!/usr/bin/env python3

"""Module containing smart contract bug classification according to
VeriSmart
"""


# Standard Library
from enum import Enum


class VeriSmartKind(Enum):
    """Class representing bug kind in VeriSmart Classification."""

    ARITHMETIC = "Arithmetic"

    LEAKING_ETHER = "Leaking Ether"

    UNSAFE_SELFDESTRUCT = "Unsafe Selfdestruct"

    def __str__(self) -> str:
        return self.value

    @staticmethod
    def elements():
        """Return all elements of VeriSmart Classification"""
        return [c.value for c in VeriSmartKind]
