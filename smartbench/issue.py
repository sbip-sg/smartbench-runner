#!/usr/bin/env python3


# Standard Library
from enum import Enum, auto
from typing import Union

# Library
from smartbench.location import Location


class IssueKind(Enum):
    """Class representing the kind of issue."""

    # Unknown
    UNKNOWN = "Unknown Issue"

    # Reentrancy
    REENTRANCY = "Reentrancy"
    REENTRANCY_READ_ONLY = "Reentrancy on Read-Only State"

    # Unchecked operations
    UNCHECKED_SEND = "Unchecked Send"
    LACK_OF_ZERO_ADDRESS_VALIDATION = "Lack of Zero-Address Validation"

    # Event operations
    SHOULD_EMIT_EVENT = "Should Emit Event"

    # Compiler
    OUTDATED_COMPILER_VERSION = "Outdated Compiler Version"
    COMPILER_NOT_RECOMMENDED_FOR_DEPLOYMENT = (
        "Compiler Not Recommended for Deployment"
    )

    # User input
    USER_CAN_MANIPULATE_ARRAY_LENGTH = "User Can Manipulate Array Length"

    # Coding style
    PARAMETER_NAME_NOT_IN_MIXED_CASE = "Parameter Name Not in Mixed Case"
    VARIABLE_NAME_NOT_IN_MIXED_CASE = "Variable Name Not in Mixed Case"
    FUNCTION_NAME_NOT_IN_MIXED_CASE = "Function Name Not in Mixed Case"
    MODIFIER_NAME_NOT_IN_MIXED_CASE = "Modifier Name Not in Mixed Case"

    # Code optimization
    MULTIPLICATION_AFTER_DIVISION = "Multiplication after Division"
    POSIBLE_UNREACHABLE_CODE = "Posible Unreachable Code"

    # Deprecated features
    DEPRECATED_THROW = "Deprecated Throw"

    def __str__(self):
        return self.value


class Severity(Enum):
    """Class representing severity level of an issue."""

    # Severity level
    UNKNOWN = "Unknown Severity"
    CODING_STYLE = "Coding Style"
    CODE_OPTIMIZATION = "Code Optimization"
    INFORMATIONAL = "Informational"
    LOW_RISK = "Low Risk"
    MEDIUM_RISK = "Medium Risk"
    HIGH_RISK = "High Risk"

    def __str__(self) -> str:
        return self.value


class Confidence(Enum):
    """Class representing confidence level of the checker when reporting the
    issue."""

    # Confidence level
    UNKNOWN = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()

    def __str__(self) -> str:
        if self == Confidence.LOW:
            return "Low Confidence"

        if self == Confidence.MEDIUM:
            return "Medium Confidence"

        if self == Confidence.HIGH:
            return "High Confidence"

        return "Unknown Confidence"


class Checker:
    """Class representing an analyzer and the checking rule that it uses."""

    analyzer: str
    rule: str

    def __init__(self, analyzer: str, rule: str):
        self.analyzer = analyzer
        self.rule = rule


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
            location = f"{self.location.print_concise()}"
        else:
            location = "Unknown location"
        return (
            f"Issue: {self.kind}\n"
            f"  + Rule: {self.checker.rule}\n"
            f"  + Severity: {self.severity}, {self.confidence}\n"
            f"  + Location: {location}\n"
        )
