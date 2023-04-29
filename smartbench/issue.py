#!/usr/bin/env python3


# Standard Library
from enum import Enum
from typing import Optional

# Library
from smartbench.bugdb.sbc import SBC
from smartbench.solidity.loc import Location


class IssueKind(Enum):
    """Class representing the kind of issue.
    + Use for all annotation and bug parsing.
    + Different bug names can map to the same issue
    """

    # Unknown
    UNKNOWN = "Unknown Issue"

    # Reentrancy
    REENTRANCY = "Reentrancy"
    REENTRANCY_READ_ONLY = "Reentrancy on Read-Only State"

    # Unchecked operations
    UNCHECKED_SEND = "Unchecked Send"
    LEAKING_ETHER = "Unchecked Send"  # alias of the same bug type
    SEND_ETH_TO_ARBITRARY_USER = "Unchecked Send"  # alias of the same bug type

    UNCHECKED_LOWLEVEL_CODE = "Unchecked Low-Level Code"
    UNHANDLED_EXCEPTION = (
        "Unchecked Low-Level Code"  # alias of the same bug type
    )

    LACK_OF_ZERO_ADDRESS_VALIDATION = "Lack of Zero-Address Validation"

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
    BLOCK_DEPENDENCY = "Block values dependency"
    USE_BLOCK_TIMESTAMP = (
        "Block values dependency"  # alias of the same bug type
    )

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

    # All issue kinds
    ASSERTION_FAILURE = "ASSERTION_FAILURE"
    ARBITRARY_WRITE = "ARBITRARY_WRITE"
    INTEGER_BUG = "ARITHMETIC_BUG"
    TRANSACTION_ORDER_DEPENDENCY = "TRANSACTION_ORDER_DEPENDENCY"
    ACCESS_CONTROL = "ACCESS_CONTROL"
    LOCKING_ETHER = "LOCKING_ETHER"
    UNSAFE_SELFDESTRUCT = "UNSAFE_SELFDESTRUCT"
    UNSAFE_DELEGATECALL = "UNSAFE_DELEGATECALL"
    TX_ORIGIN_USAGE = "TX_ORIGIN_USAGE"
    REQUIREMENT_VIOLATION = "REQUIREMENT_VIOLATION"

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other.value


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
    UNKNOWN = "Unknown Confidence"
    LOW_CONFIDENCE = "Low Confidence"
    MEDIUM_CONFIDENCE = "Medium Confidence"
    HIGH_CONFIDENCE = "High Confidence"

    def __str__(self) -> str:
        return self.value


class Checker:
    """Class representing an analyzer and the checking rule that it uses."""

    def __init__(self, analyzer: str, detector: str):
        self.analyzer: str = analyzer
        self.detector: str = detector


class Issue:
    """Class representing an issue found in smart contracts."""

    # Shared index counter for all issues.
    # This counter needs to be reset for each test file.
    index_counter: int = 1

    def __init__(
        self,
        issue_kind: IssueKind,
        description: str,
        severity: Severity,
        confidence: Confidence,
        location: Optional[Location],
        checker: Checker,
    ):
        """Constructor."""
        # Initialize all instance variables
        self.issue_kind: IssueKind = issue_kind
        self.description: str = description
        self.severity: Severity = severity
        self.confidence: Confidence = confidence
        self.location: Optional[Location] = location
        self.checker: Checker = checker
        self.sbc: Optional[SBC] = classify_issue_kind_to_sbc(issue_kind)

        # Assign an index to the issue. This index is unique for all issues in
        # the same contract
        self.index = Issue.index_counter
        Issue.index_counter += 1

    def __str__(self):
        location = (
            f"{self.location.print_concise()}"
            if self.location
            else "Unknown Location"
        )
        analyzer = self.checker.analyzer
        detector = self.checker.detector
        return (
            f"Issue ({self.index}): {self.issue_kind}\n"
            f"  + Checker: {analyzer} --> {detector}\n"
            f"  + SmartBugs Classification: {self.sbc}\n"
            f"  + Severity: {self.severity}, {self.confidence}\n"
            f"  + Location: {location}\n"
        )

    def __eq__(self, other):
        return (
            self.issue_kind == other.issue_kind
            and self.location == other.location
            and self.severity == other.severity
        )

    def __ne__(self, other):
        return not (self.__eq__(other))


def classify_issue_kind_to_sbc(
    issue_kind: IssueKind,
) -> Optional[SBC]:
    """Classify an issue kind to a bug kind in SmartBugs classification."""
    if issue_kind in []:
        return SBC.ACCESS_CONTROL

    if issue_kind in []:
        return SBC.ARITHMETIC

    if issue_kind in []:
        return SBC.BAD_RANDOMNESS

    if issue_kind in []:
        return SBC.DENIAL_OF_SERVICE

    if issue_kind in []:
        return SBC.FRONT_RUNNING

    if issue_kind in [IssueKind.REENTRANCY, IssueKind.REENTRANCY_READ_ONLY]:
        return SBC.REENTRANCY

    if issue_kind in []:
        return SBC.SHORT_ADDRESSES

    if issue_kind in [
        IssueKind.BLOCK_DEPENDENCY,
        IssueKind.USE_BLOCK_TIMESTAMP,
    ]:
        return SBC.TIME_MANIPULATION

    if issue_kind in [
        IssueKind.UNHANDLED_EXCEPTION,
        IssueKind.UNCHECKED_LOWLEVEL_CODE,
    ]:
        return SBC.UNCHECKED_LOW_LEVEL_CALLS

    # Not matching any SmartBugs Classification
    return None
