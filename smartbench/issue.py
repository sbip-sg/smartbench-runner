#!/usr/bin/env python3


# Standard Library
from enum import Enum
from typing import List, Optional

# Library
from smartbench.bugdb.sbc import SmartBugsPP
from smartbench.bugdb.sdc import SolidiFIPP
from smartbench.bugdb.smartbench import SmartbenchKind
from smartbench.bugdb.swc import SWCKind
from smartbench.bugdb.verismart import VeriSmartKind
from smartbench.solidity import loc
from smartbench.solidity.loc import Location


class IssueKind(Enum):
    """Class representing the kind of issue.
    + Use for all annotation and bug parsing.
    + Different bug names can map to the same issue
    """

    ##############################
    # Security Vulnerabilities

    # Reentrancy, SWC-107
    REENTRANCY = "Reentrancy"
    REENTRANCY_READ_ONLY = "Reentrancy on Read-Only State"

    # Unchecked calls
    UNCHECKED_SEND_ETHER = "Unchecked Send Ether"
    UNCHECKED_TRANSFER_ETHER = "Unchecked Transfer Ether"
    UNCHECKED_CALL_RETURN_VALUE = "Unchecked Call Return Value"
    UNUSED_RETURN_VALUE = "Unused Return Value"

    # Exceptions
    UNHANDLED_EXCEPTION = "Unhandled Exception"

    # Leaking Ether
    LEAKING_ETHER = "Leaking Ether"

    # Locking Ether
    LOCKING_ETHER = "Locking Ether"

    # Validation
    LACK_OF_ZERO_ADDRESS_VALIDATION = "Lack of Zero-Address Validation"

    # External calls
    ARBITRARY_EXTERNAL_CALL = "Arbitrary External Call"

    POSSIBLY_UNINITIALIZED = "POSSIBLY_UNINITIALIZED"
    # Low-level code
    UNCHECKED_LOW_LEVEL_CODE = "Unchecked Low-Level Code"
    LOW_LEVEL_CALL = "Low-Level Call"
    USE_ASSEMBLY = "Use Assembly"

    # Event operations
    SHOULD_EMIT_EVENT = "Should Emit Event"

    # Interface
    INCORRECT_ERC20_FUNCTION_INTERFACE = "Incorrect ERC20 Function Interface"

    # Compiler
    OUTDATED_COMPILER_VERSION = "Outdated Compiler Version"
    VULNERABLE_COMPILER_VERSION = "Vulnerable Compiler Version"
    COMPILER_NOT_RECOMMENDED_FOR_DEPLOYMENT = (
        "Compiler Not Recommended for Deployment"
    )

    # Logic
    WEAK_PSEUDO_RANDOM_NUMBER_GENERATOR = "Weak Pseudo Random Number Generator"
    DANGEROUS_STRICT_EQUALITY = "Dangerous Strict Equality"

    # User input
    USER_CAN_MANIPULATE_ARRAY_LENGTH = "User Can Manipulate Array Length"

    # Initialization
    UNINITIALIZED_STATE_VARIABLE = "Uninitialized State Variable"
    UNINITIALIZED_STORAGE_VARIABLE = "Uninitialized Storage Variable"
    UNINITIALIZED_LOCAL_VARIABLE = "Uninitialized Local Variable"
    FUNCTION_INIT_NON_CONSTANT_STATE = "Function Init with Non-Constant State"

    # Inheritance
    MISSING_INHERITANCE = "Missing Inheritance"

    # Backdoor
    BACKDOOR_FUNCTION = "Backdoor Function"

    # Code complexity
    EXTERNAL_CALLS_INSIDE_LOOP = "External Calls Inside Loop"

    # Deprecated features
    DEPRECATED_THROW = "Deprecated Throw"
    DEPRECATED_SUICIDE = "Deprecated Suicide"
    DEPRECATED_MSG_GAS = "Deprecated msg.gas"
    DEPRECATED_SHA3 = "Deprecated SHA3"
    DEPRECATED_BLOCK_DOT_BLOCKHASH = "Deprecated block.blockhash()"

    # Integer bugs
    INTEGER_BUG = "Integer Bug"
    INTEGER_OVERFLOW = "Integer Overflow"
    INTEGER_UNDERFLOW = "Integer Underflow"
    INTEGER_TRUNCATION = "Integer Truncation"
    DIVISION_BY_ZERO = "Division by Zero"

    # SWC-110, assertion
    ASSERTION_FAILURE = "Assertion Failure"

    # SWC-124
    WRITE_TO_ARBITRARY_STORAGE_LOCATION = "Write to Arbitrary Storage Location"

    # SWC-113
    DENIAL_OF_SERVICE_WITH_FAILED_CALL = "Denial of Service with Failed Call"
    DENIAL_OF_SERVICE = "Denial of Service"

    # SWC-115
    AUTHORIZATION_THROUGH_TX_ORIGIN = "Authorization through tx.origin"

    # SWC-116
    BLOCK_VALUE_DEPENDENCY = "Block Values Dependency"

    FRONT_RUNNING = "Front Running"
    TRANSACTION_ORDER_DEPENDENCY = "Transaction Order Dependency"

    ACCESS_CONTROL = "Access Control"

    UNSAFE_SELFDESTRUCT = "Unsafe Selfdestruct"

    # SWC-112
    UNSAFE_DELEGATECALL = "Unsafe DelegateCall"

    REQUIREMENT_VIOLATION = "Requirement Violation"

    VIEW_FUNCTION_CONTAIN_ASM = "View Function Contains Assembly Code"

    ##############################
    # Coding style

    PARAMETER_NAME_NOT_IN_MIXED_CASE = "Parameter Name Not in Mixed Case"
    VARIABLE_NAME_NOT_IN_MIXED_CASE = "Variable Name Not in Mixed Case"
    FUNCTION_NAME_NOT_IN_MIXED_CASE = "Function Name Not in Mixed Case"
    MODIFIER_NAME_NOT_IN_MIXED_CASE = "Modifier Name Not in Mixed Case"
    CONSTANT_NAME_NOT_IN_UPPER_CASE = "Constant Name Not in Upper Case"
    CONTRACT_NAME_NOT_IN_CAP_WORDS = "Contract Name Not in CapWords"
    STRUCT_NAME_NOT_IN_CAP_WORDS = "Struct Name Not in CapWords"
    EVENT_NAME_NOT_IN_CAP_WORDS = "Event Name Not in CapWords"

    SHADOWING_LOCAL_VARIABLE = "Shadowing Local Variable"
    SHADOWING_STATE_VARIABLE = "Shadowing State Variable"
    SHADOWING_ABSTRACT_FUNCTION = "Shadowing Abstract Function"
    SHADOWING_BUILTIN_SYMBOL = "Shadowing Built-in Symbol"

    SIMILAR_VARIABLE_NAME = "Similar Variable Name"

    ##############################
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
    TAUTOLOGY_OR_CONTRADICTION = "Tautology or Contradiction"
    REDUNDANT_EXPRESSION = "Redundant Expression"

    ##############################
    # Unknown

    UNKNOWN = "Unknown Issue"

    def __str__(self):
        return self.value

    def __eq__(self, other):
        return other and self.value == other.value
    def __hash__(self):
        return hash(self.value)

class Severity(Enum):
    """Class representing severity level of an issue."""

    # Severity level
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

    def __str__(self) -> str:
        return f"{self.analyzer} --> {self.detector}"


class Issue:
    """Class representing an issue found in smart contracts."""

    # Shared index counter for all issues.
    # This counter needs to be reset for each test file.
    index_counter: int = 1

    def __init__(
        self,
        issue_kind: IssueKind,
        description: str,
        locations: List[Location],
        checker: Checker,
        severity: Optional[Severity] = None,
        confidence: Optional[Confidence] = None,
        time_detected: int = 0,
    ):
        """Constructor."""
        self.issue_kind: IssueKind = issue_kind
        self.description: str = description
        self.severity: Optional[Severity] = severity
        self.confidence: Optional[Confidence] = confidence

        # Time in second when the issue is detected
        self.detected_time: Optional[int] = time_detected

        # Use a list of locations to support tools that reports multiple
        # potential bug locations of an issue.
        self.locations: List[Location] = locations

        self.time_detected: int =  time_detected # Time in seconds when the issue is found.

        self.checker: Checker = checker

        # Classify to SWC classification
        self.swc_kind: Optional[SWCKind] = classify_to_swc_kind(issue_kind)

        # Classify to SmartBugs++ classification
        self.smartbugs_pp_kind: Optional[
            SmartBugsPP
        ] = classify_to_smartbugs_pp_kind(issue_kind)

        # Classify to SolidiFI classification
        self.solidifi_pp_kind: Optional[
            SolidiFIPP
        ] = classify_to_solidifi_pp_kind(issue_kind)

        # Classify to Smartbench classification
        self.smartbench_kind: Optional[
            SmartbenchKind
        ] = classify_to_smartbench_kind(issue_kind)

        # Classify to VeriSmart classification
        self.verismart_kind: Optional[
            VeriSmartKind
        ] = classify_to_verismart_kind(issue_kind)

        # Assign an index to the issue. This index is unique for all issues in
        # the same contract
        self.index = Issue.index_counter
        Issue.index_counter += 1

    def __str__(self):
        location = (
            f"{loc.print_concise_locations(self.locations)}"
            if self.locations
            else "Unknown Location"
        )
        return f"Issue ({self.index}): {self.issue_kind} ({location})\n"

    def __eq__(self, other):
        return (
            self.issue_kind == other.issue_kind
            and self.locations == other.locations
            and self.severity == other.severity
        )

    def to_json(self):
        return self.index, self.time_detected

    def __ne__(self, other):
        return not (self.__eq__(other))

    def pretty_print(
        self,
        print_swc_kind: bool = True,
        print_smartbugs_kind: bool = True,
        print_solidifi_kind: bool = True,
        print_concise: bool = True,
    ) -> str:
        location = (
            f"{loc.print_concise_locations(self.locations)}"
            if self.locations
            else "Unknown Location"
        )

        if print_concise:
            issue_str = (
                f"Issue ({self.index}): {self.issue_kind} ({location})\n"
            )
            if print_swc_kind:
                issue_str += f"  SWC: {self.swc_kind}"
            if print_smartbugs_kind:
                issue_str += f", SmartBugs++: {self.smartbugs_pp_kind}"
            if print_solidifi_kind:
                issue_str += f",  SolidiFI: {self.solidifi_pp_kind}"
            return issue_str
        else:
            issue_str = f"Issue ({self.index}): {self.issue_kind}\n"
            issue_str += f"  + Checker: {self.checker}\n"
            if print_swc_kind:
                issue_str += f"  + SWC Kind: {self.swc_kind}\n"
            if print_smartbugs_kind:
                issue_str += f"  + SmartBugs++ Kind: {self.smartbugs_pp_kind}\n"
            if print_solidifi_kind:
                issue_str += f"  + SolidiFI Kind: {self.solidifi_pp_kind}\n"
            if self.detected_time is not None:
                issue_str += f"  + Detected time: {self.detected_time}\n"
            issue_str += f"  + Location: {location}"
            return issue_str


def record_new_issue_and_deduplicate(
    existing_issues: List[Issue],
    issue_kind: IssueKind,
    description: str,
    locations: List[Location],
    checker: Checker,
    severity: Optional[Severity] = None,
    confidence: Optional[Confidence] = None,
    detected_time: Optional[int] = None,
):
    # Check if the new issue is already reported
    for issue in existing_issues:
        if issue.issue_kind == issue_kind and loc.check_same_locations(
            issue.locations, locations
        ):
            return existing_issues

    # Create new issue and collect it
    issue = Issue(
        issue_kind,
        description,
        locations,
        checker,
        severity,
        confidence,
        detected_time,
    )
    existing_issues.append(issue)
    return existing_issues


def classify_to_smartbugs_pp_kind(
    issue_kind: IssueKind,
) -> Optional[SmartBugsPP]:
    """Classify an issue kind to a bug kind in SmartBugs++ classification."""
    if issue_kind in [
        IssueKind.ACCESS_CONTROL,
        IssueKind.UNSAFE_DELEGATECALL,
        IssueKind.AUTHORIZATION_THROUGH_TX_ORIGIN,
    ]:
        return SmartBugsPP.ACCESS_CONTROL

    if issue_kind in [
        IssueKind.INTEGER_BUG,
        IssueKind.INTEGER_OVERFLOW,
        IssueKind.INTEGER_UNDERFLOW,
        IssueKind.INTEGER_TRUNCATION,
    ]:
        return SmartBugsPP.ARITHMETIC

    if issue_kind in [IssueKind.ASSERTION_FAILURE]:
        return SmartBugsPP.ASSERTION_FAILURE

    if issue_kind in [IssueKind.BLOCK_VALUE_DEPENDENCY]:
        return SmartBugsPP.BLOCK_DEPENDENCY

    if issue_kind in [
        IssueKind.DENIAL_OF_SERVICE_WITH_FAILED_CALL,
        IssueKind.DENIAL_OF_SERVICE,
    ]:
        return SmartBugsPP.DENIAL_OF_SERVICE

    if issue_kind in [
        IssueKind.FRONT_RUNNING,
        IssueKind.TRANSACTION_ORDER_DEPENDENCY,
    ]:
        return SmartBugsPP.FRONT_RUNNING

    if issue_kind in [
        IssueKind.LEAKING_ETHER,
        IssueKind.UNCHECKED_SEND_ETHER,
        IssueKind.UNCHECKED_TRANSFER_ETHER,
    ]:
        return SmartBugsPP.LEAKING_ETHER

    if issue_kind in [IssueKind.LOCKING_ETHER]:
        return SmartBugsPP.LOCKING_ETHER

    if issue_kind in [IssueKind.REENTRANCY, IssueKind.REENTRANCY_READ_ONLY]:
        return SmartBugsPP.REENTRANCY

    if issue_kind in []:
        return SmartBugsPP.SHORT_ADDRESSES

    if issue_kind in [
        IssueKind.UNCHECKED_CALL_RETURN_VALUE,
        IssueKind.UNCHECKED_LOW_LEVEL_CODE,
        IssueKind.UNHANDLED_EXCEPTION,
    ]:
        return SmartBugsPP.UNHANDLED_EXCEPTION

    if issue_kind in [IssueKind.UNSAFE_SELFDESTRUCT]:
        return SmartBugsPP.UNPROTECTED_SELFDESTRUCT

    # Not matching any SmartBugs++ Kind
    return None


def classify_to_solidifi_pp_kind(
    issue_kind: IssueKind,
) -> Optional[SolidiFIPP]:
    """Classify an issue kind to a bug kind in SolidiFI classification."""
    if issue_kind in [
        IssueKind.INTEGER_BUG,
        IssueKind.INTEGER_OVERFLOW,
        IssueKind.INTEGER_UNDERFLOW,
        IssueKind.INTEGER_TRUNCATION,
    ]:
        return SolidiFIPP.OVERFLOW_UNDERFLOW

    if issue_kind in [IssueKind.REENTRANCY, IssueKind.REENTRANCY_READ_ONLY]:
        return SolidiFIPP.REENTRANCY

    if issue_kind in [IssueKind.BLOCK_VALUE_DEPENDENCY]:
        return SolidiFIPP.TIMESTAMP_DEPENDENCY

    if issue_kind in [IssueKind.UNCHECKED_SEND_ETHER, IssueKind.LEAKING_ETHER]:
        return SolidiFIPP.UNCHECKED_SEND

    if issue_kind in [
        IssueKind.UNCHECKED_CALL_RETURN_VALUE,
        IssueKind.UNCHECKED_LOW_LEVEL_CODE,
        IssueKind.UNHANDLED_EXCEPTION,
    ]:
        return SolidiFIPP.UNHANDLED_EXCEPTION

    if issue_kind in [
        IssueKind.AUTHORIZATION_THROUGH_TX_ORIGIN,
    ]:
        return SolidiFIPP.TX_ORIGIN

    # Not matching any SolidiFI Kind
    return None


def classify_to_smartbench_kind(
    issue_kind: IssueKind,
) -> Optional[SmartbenchKind]:
    """Classify an issue kind to a bug kind in Smartbench classification."""
    if issue_kind in [IssueKind.ACCESS_CONTROL, IssueKind.UNSAFE_DELEGATECALL, IssueKind.ARBITRARY_EXTERNAL_CALL]:
        return SmartbenchKind.ACCESS_CONTROL

    if issue_kind in [IssueKind.REENTRANCY, IssueKind.REENTRANCY_READ_ONLY]:
        return SmartbenchKind.REENTRANCY

    if issue_kind in [IssueKind.LACK_OF_ZERO_ADDRESS_VALIDATION]:
        return SmartbenchKind.ADDRESS_VALIDATION

    if issue_kind in [
        IssueKind.INTEGER_BUG,
        IssueKind.INTEGER_OVERFLOW,
        IssueKind.INTEGER_UNDERFLOW,
        IssueKind.INTEGER_TRUNCATION,
    ]:
        return SmartbenchKind.ARITHMETIC

    # Not matching any Smartbench Kind
    return None


def classify_to_verismart_kind(
    issue_kind: IssueKind,
) -> Optional[VeriSmartKind]:
    """Classify an issue kind to a bug kind in VeriSmart classification."""
    if issue_kind in [
        IssueKind.INTEGER_BUG,
        IssueKind.INTEGER_OVERFLOW,
        IssueKind.INTEGER_UNDERFLOW,
        IssueKind.INTEGER_TRUNCATION,
    ]:
        return VeriSmartKind.ARITHMETIC

    if issue_kind in [
        IssueKind.LEAKING_ETHER,
        IssueKind.UNCHECKED_SEND_ETHER,
        IssueKind.UNCHECKED_TRANSFER_ETHER,
    ]:
        return VeriSmartKind.LEAKING_ETHER

    if issue_kind in [IssueKind.UNSAFE_SELFDESTRUCT]:
        return VeriSmartKind.UNSAFE_SELFDESTRUCT

    # Not matching any VeriSmart Kind
    return None


def classify_to_swc_kind(
    issue_kind: IssueKind,
) -> Optional[SWCKind]:
    """Classify an issue kind to a bug kind in SmartBugs++ classification."""

    if issue_kind in []:
        return SWCKind.FUNCTION_DEFAULT_VISIBILITY

    if issue_kind in [
        IssueKind.INTEGER_OVERFLOW,
        IssueKind.INTEGER_UNDERFLOW,
        IssueKind.INTEGER_TRUNCATION,
        IssueKind.INTEGER_BUG,
    ]:
        return SWCKind.INTEGER_OVERFLOW_UNDERFLOW

    if issue_kind in []:
        return SWCKind.OUTDATED_COMPILER_VERSION

    if issue_kind in []:
        return SWCKind.FLOATING_PRAGMA

    if issue_kind in [
        IssueKind.UNCHECKED_CALL_RETURN_VALUE,
        IssueKind.UNCHECKED_SEND_ETHER,
    ]:
        return SWCKind.UNCHECKED_CALL_RETURN_VALUE

    if issue_kind in [IssueKind.LEAKING_ETHER]:
        return SWCKind.UNPROTECTED_ETHER_WITHDRAWAL

    if issue_kind in [IssueKind.UNSAFE_SELFDESTRUCT]:
        return SWCKind.UNPROTECTED_SELFDESTRUCT_INSTRUCTION

    if issue_kind in [IssueKind.REENTRANCY, IssueKind.REENTRANCY_READ_ONLY]:
        return SWCKind.REENTRANCY

    if issue_kind in []:
        return SWCKind.STATE_VARIABLE_DEFAULT_VISIBILITY

    if issue_kind in []:
        return SWCKind.UNINITIALIZED_STORAGE_POINTER

    if issue_kind in [IssueKind.ASSERTION_FAILURE]:
        return SWCKind.ASSERT_VIOLATION

    if issue_kind in []:
        return SWCKind.USE_OF_DEPRECATED_SOLIDITY_FUNCTIONS

    if issue_kind in [IssueKind.UNSAFE_DELEGATECALL]:
        return SWCKind.DELEGATECALL_TO_UNTRUSTED_CALLEE

    if issue_kind in [
        IssueKind.DENIAL_OF_SERVICE_WITH_FAILED_CALL,
        IssueKind.DENIAL_OF_SERVICE,
    ]:
        return SWCKind.DOS_WITH_FAILED_CALL

    if issue_kind in [
        IssueKind.TRANSACTION_ORDER_DEPENDENCY,
        IssueKind.FRONT_RUNNING,
    ]:
        return SWCKind.TRANSACTION_ORDER_DEPENDENCE

    if issue_kind in [IssueKind.AUTHORIZATION_THROUGH_TX_ORIGIN]:
        return SWCKind.AUTHORIZATION_THROUGH_TX_ORIGIN

    if issue_kind in [IssueKind.BLOCK_VALUE_DEPENDENCY]:
        return SWCKind.BLOCK_VALUES_AS_A_PROXY_FOR_TIME

    if issue_kind in []:
        return SWCKind.SIGNATURE_MALLEABILITY

    if issue_kind in []:
        return SWCKind.INCORRECT_CONSTRUCTOR_NAME

    if issue_kind in []:
        return SWCKind.SHADOWING_STATE_VARIABLES

    if issue_kind in []:
        return SWCKind.WEAK_SOURCES_OF_RANDOMNESS_FROM_CHAIN_ATTRIBUTES

    if issue_kind in []:
        return SWCKind.MISSING_PROTECTION_AGAINST_SIGNATURE_REPLAY_ATTACKS

    if issue_kind in []:
        return SWCKind.LACK_OF_PROPER_SIGNATURE_VERIFICATION

    if issue_kind in [IssueKind.REQUIREMENT_VIOLATION]:
        return SWCKind.REQUIREMENT_VIOLATION

    if issue_kind in [IssueKind.WRITE_TO_ARBITRARY_STORAGE_LOCATION]:
        return SWCKind.WRITE_TO_ARBITRARY_STORAGE_LOCATION

    if issue_kind in []:
        return SWCKind.INCORRECT_INHERITANCE_ORDER

    if issue_kind in []:
        return SWCKind.INSUFFICIENT_GAS_GRIEFING

    if issue_kind in []:
        return SWCKind.ARBITRARY_JUMP_WITH_FUNCTION_TYPE_VARIABLE

    if issue_kind in []:
        return SWCKind.DOS_WITH_BLOCK_GAS_LIMIT

    if issue_kind in []:
        return SWCKind.TYPOGRAPHICAL_ERROR

    if issue_kind in []:
        return SWCKind.RIGHT_TO_LEFT_OVERRIDE_CONTROL_CHARACTER

    if issue_kind in []:
        return SWCKind.PRESENCE_OF_UNUSED_VARIABLES

    if issue_kind in []:
        return SWCKind.UNEXPECTED_ETHER_BALANCE

    if issue_kind in []:
        return SWCKind.HASH_COLLISIONS_WITH_MULTIPLE_VARIABLE_LENGTH_ARGUMENTS

    if issue_kind in []:
        return SWCKind.MESSAGE_CALL_WITH_HARDCODED_GAS_AMOUNT

    if issue_kind in []:
        return SWCKind.CODE_WITH_NO_EFFECTS

    if issue_kind in []:
        return SWCKind.UNENCRYPTED_PRIVATE_DATA_ON_CHAIN

    return None
