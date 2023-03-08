#!/usr/bin/env python3

# Standard Library
import os

from enum import Enum, auto
from typing import Union

# Library
from smartbench.location import Location


class IssueKind(Enum):
    """Class representing the kind of issue."""

    # Unknown
    UNKNOWN = auto()

    # Reentrancy
    REENTRANCY = auto()
    REENTRANCY_READ_ONLY = auto()

    # Deprecated features
    DEPRECATED_THROW = auto()


class Severity(Enum):
    """Class representing severity level of an issue."""

    # Severity level
    UNKNOWN = auto()
    CODING_STYLE = auto()
    OPTIMIZATION = auto()
    INFORMATIONAL = auto()
    LOW_RISK = auto()
    MEDIUM_RISK = auto()
    HIGH_RISK = auto()


class Confidence(Enum):
    """Class representing confidence level of the checker when reporting the
    issue."""

    # Confidence level
    UNKNOWN = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()


class Checker:
    """Class representing an issue checker and its setting."""

    analyzer: str
    settings: str

    def __init__(self, analyzer: str, settings: str):
        self.analyzer = analyzer
        self.settings = settings


class Issue:
    """Class representing an issue found in smart contracts."""

    # Attributes of an issue
    kind: IssueKind
    description: str
    severity: Severity
    confidence: Confidence
    location: Union[Location, None]
    checker: Checker

    def __init__(
        self, kind, description, severity, confidence, location, checker
    ):
        """Constructor."""
        self.kind = kind
        self.description = description
        self.severity = severity
        self.confidence = confidence
        self.location = location
        self.checker = checker

    def __str__(self):
        if self.location:
            file_name = os.path.basename(self.location.file_path)
            line_column = self.location.get_line_column_info()
            location = f"{file_name}:{line_column}"
        else:
            location = "Unknown"
        return (
            f"{self.kind} -- {self.severity} -- {self.confidence} @ {location}"
        )
