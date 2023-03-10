#!/usr/bin/env python3


# Standard Library
from enum import Enum, auto
from typing import List, Union

# Library
from smartbench.bug_annot import BugAnnot
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
    UNCHECKED_LOWLEVEL_CODE = "Unchecked Low-Level Code"
    LACK_OF_ZERO_ADDRESS_VALIDATION = "Lack of Zero-Address Validation"
    SEND_ETH_TO_ARBITRARY_USER = "Arbitrary Send ETH"

    # Low-level code
    LOW_LEVEL_CALL = "Low-Level Call"

    # Event operations
    SHOULD_EMIT_EVENT = "Should Emit Event"

    # Interface
    INCORRECT_ERC20_FUNCTION_INTERFACE = "Incorrect ERC20 Function Interface"

    # Compiler
    OUTDATED_COMPILER_VERSION = "Outdated Compiler Version"
    COMPILER_NOT_RECOMMENDED_FOR_DEPLOYMENT = (
        "Compiler Not Recommended for Deployment"
    )

    # Logic
    WEAK_PSEUDO_RANDOM_NUMBER_GENERATOR = "Weak Pseudo Random Number Generator"
    DANGEROUS_STRICT_EQUALITY = "Dangerous Strict Equality"

    # Weak feature
    USE_BLOCK_TIMESTAMP = "Use Block Timestamp"

    # User input
    USER_CAN_MANIPULATE_ARRAY_LENGTH = "User Can Manipulate Array Length"

    # Initialization
    UNINITIALIZED_STORAGE = "Uninitialized Storage"

    # Coding style
    PARAMETER_NAME_NOT_IN_MIXED_CASE = "Parameter Name Not in Mixed Case"
    VARIABLE_NAME_NOT_IN_MIXED_CASE = "Variable Name Not in Mixed Case"
    FUNCTION_NAME_NOT_IN_MIXED_CASE = "Function Name Not in Mixed Case"
    MODIFIER_NAME_NOT_IN_MIXED_CASE = "Modifier Name Not in Mixed Case"
    CONSTANT_NAME_NOT_IN_UPPER_CASE = "Constant Name Not in Upper Case"
    SHADOWING_LOCAL_VARIABLE = "Shadowing Variable"

    # Code optimization
    MULTIPLICATION_AFTER_DIVISION = "Multiplication after Division"
    POSIBLE_UNREACHABLE_CODE = "Posible Unreachable Code"
    UNUSED_FUNCTION = "Unused Function"
    UNUSED_VARIABLE = "Unused Variable"
    USE_LITERALS_WITH_TOO_MANY_DIGITS = "Literal with Too Many Digits"
    USE_CONSTANT_INSTEAD_OF_VARIABLE = "Use Constant Instead of Variable"
    FUNCTION_SHOULD_BE_DECLARED_EXTERNAL = (
        "Function Should Be Declared External"
    )
    COMPARE_TO_BOOLEAN_CONSTANT = "Compare to Boolean Constant"
    COSTLY_LOOP = "Costly Loop"

    # Deprecated features
    DEPRECATED_THROW = "Deprecated Throw"
    DEPRECATED_SHA3 = "Deprecated SHA3"
    DEPRECATED_BLOCK_DOT_BLOCKHASH = "Deprecated block.blockhash()"

    def __str__(self):
        return self.value


class Severity(Enum):
    """Class representing severity level of an issue."""

    # Severity level
    UNKNOWN = "Unknown Severity"
    CODING_STYLE = "Coding Style"
    CODE_OPTIMIZATION = "Optimization"
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
    detector: str

    def __init__(self, analyzer: str, detector: str):
        self.analyzer = analyzer
        self.detector = detector


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
        location = (
            f"{self.location.print_concise()}"
            if self.location
            else "Unknown Location"
        )
        analyzer = self.checker.analyzer
        detector = self.checker.detector
        return (
            f"Issue: {self.kind}\n"
            f"  + Checker: {analyzer} --> {detector}\n"
            f"  + Severity: {self.severity}, {self.confidence}\n"
            f"  + Location: {location}\n"
        )

    def validate(self, bug_annots: List[BugAnnot]) -> bool:
        """Validate if the issue matches one of the bug annotations."""
        # TODO: implement
        return False
