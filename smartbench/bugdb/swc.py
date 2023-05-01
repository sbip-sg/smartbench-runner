#!/usr/bin/env python3

"""Module handling smart contract SWCs."""

# Standard Library
import json
import os

from dataclasses import dataclass
from enum import Enum
from typing import List

# Library
from smartbench.printer import safe_print


SMARTBENCH_DIR = os.path.dirname(__file__)
PROJECT_ROOT_DIR = os.path.dirname(SMARTBENCH_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT_DIR, "data")


class SWCKind(Enum):
    """Class modelling a SWC Kind"""

    # SWC-100
    FUNCTION_DEFAULT_VISIBILITY = "Function Default Visibility"

    # SWC-101
    INTEGER_OVERFLOW_UNDERFLOW = "Integer Overflow and Underflow"

    # SWC-102
    OUTDATED_COMPILER_VERSION = "Outdated Compiler Version"

    # SWC-103
    FLOATING_PRAGMA = "Floating Pragma"

    # SWC-104
    UNCHECKED_CALL_RETURN_VALUE = "Unchecked Call Return Value"

    # SWC-105
    UNPROTECTED_ETHER_WITHDRAWAL = "Unprotected Ether Withdrawal"

    # SWC-106
    UNPROTECTED_SELFDESTRUCT_INSTRUCTION = (
        "Unprotected SelfDestruct Instruction"
    )

    # SWC-107
    REENTRANCY = "Reentrancy"

    # SWC-108
    STATE_VARIABLE_DEFAULT_VISIBILITY = "State Variable Default Visibility"

    # SWC-109
    UNINITIALIZED_STORAGE_POINTER = "Uninitialized Storage Pointer"

    # SWC-110
    ASSERT_VIOLATION = "Assert Violation"

    # SWC-111
    USE_OF_DEPRECATED_SOLIDITY_FUNCTIONS = (
        "Use of Deprecated Solidity Functions"
    )

    # SWC-112
    DELEGATECALL_TO_UNTRUSTED_CALLEE = "Delegatecall to Untrusted Callee"

    # SWC-113
    DOS_WITH_FAILED_CALL = "DoS with Failed Call"

    # SWC-114
    TRANSACTION_ORDER_DEPENDENCE = "Transaction Order Dependence"

    # SWC-115
    AUTHORIZATION_THROUGH_TX_ORIGIN = "Authorization through tx.origin"

    # SWC-116
    BLOCK_VALUES_AS_A_PROXY_FOR_TIME = "Block Values as a Proxy for Time"

    # SWC-117
    SIGNATURE_MALLEABILITY = "Signature Malleability"

    # SWC-118
    INCORRECT_CONSTRUCTOR_NAME = "Incorrect Constructor Name"

    # SWC-119
    SHADOWING_STATE_VARIABLES = "Shadowing State Variables"

    # SWC-120
    WEAK_SOURCES_OF_RANDOMNESS_FROM_CHAIN_ATTRIBUTES = (
        "Weak Sources of Randomness from Chain Attributes"
    )

    # SWC-121
    MISSING_PROTECTION_AGAINST_SIGNATURE_REPLAY_ATTACKS = (
        "Missing Protection against Signature Replay Attacks"
    )

    # SWC-122
    LACK_OF_PROPER_SIGNATURE_VERIFICATION = (
        "Lack of Proper Signature Verification"
    )

    # SWC-123
    REQUIREMENT_VIOLATION = "Requirement Violation"

    # SWC-124
    WRITE_TO_ARBITRARY_STORAGE_LOCATION = "Write to Arbitrary Storage Location"

    # SWC-125
    INCORRECT_INHERITANCE_ORDER = "Incorrect Inheritance Order"

    # SWC-126
    INSUFFICIENT_GAS_GRIEFING = "Insufficient Gas Griefing"

    # SWC-127
    ARBITRARY_JUMP_WITH_FUNCTION_TYPE_VARIABLE = (
        "Arbitrary Jump with Function Type Variable"
    )

    # SWC-128
    DOS_WITH_BLOCK_GAS_LIMIT = "DoS With Block Gas Limit"

    # SWC-129
    TYPOGRAPHICAL_ERROR = "Typographical Error"

    # SWC-130
    RIGHT_TO_LEFT_OVERRIDE_CONTROL_CHARACTER = (
        "Right-To-Left-Override control character (U+202E)"
    )

    # SWC-131
    PRESENCE_OF_UNUSED_VARIABLES = "Presence of Unused Variables"

    # SWC-132
    UNEXPECTED_ETHER_BALANCE = "Unexpected Ether Balance"

    # SWC-133
    HASH_COLLISIONS_WITH_MULTIPLE_VARIABLE_LENGTH_ARGUMENTS = (
        "Hash Collisions With Multiple Variable Length Arguments"
    )

    # SWC-134
    MESSAGE_CALL_WITH_HARDCODED_GAS_AMOUNT = (
        "Message Call with Hardcoded Gas Amount"
    )

    # SWC-135
    CODE_WITH_NO_EFFECTS = "Code with No Effects"

    # SWC-136
    UNENCRYPTED_PRIVATE_DATA_ON_CHAIN = "Unencrypted Private Data On-Chain"

    def __str__(self) -> str:
        return self.value


@dataclass
class SWCInfo:
    """Class modelling a SWC."""

    # Attributes
    id: str
    title: str
    description: str
    remediation: str
    relationships: List[str]
    reference: str


if __name__ == "__main__":
    safe_print(f"Smartbench dir: {SMARTBENCH_DIR}")
    safe_print(f"Data dir: {DATA_DIR}")

    swc_file = os.path.join(DATA_DIR, "swc.json")

    with open(swc_file, "r", encoding="utf-8") as file:
        try:
            swcs = json.load(file, object_hook=lambda obj: SWCInfo(**obj))
            safe_print(f"#SWCs: {len(swcs)}")
            for swc in swcs:
                safe_print(f"- {swc.id}: {swc.title}")
        except ValueError:
            safe_print("Failed to parse SWC file:", swc_file)

    if swcs is None:
        safe_print("Failed to parse SWC file:", swc_file)
