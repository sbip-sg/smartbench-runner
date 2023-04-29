#!/usr/bin/env python3

"Module representing a bug annotation."

# Standard Library
import csv
import os
import warnings

from enum import Enum
from typing import List, Optional

# Library
from smartbench.bugdb.sbc import SBC
from smartbench.issue import IssueKind
from smartbench.printer import warning, safe_print


# SmartBugs annotations
YES_TAG = "<yes>"
NO_TAG = "<no>"
REPORT_TAG = "<report>"
COMMENT_TAG = "//"

# SmartBench annotations
BUG_OPEN_TAG = "<bug "
BUG_CLOSE_TAG = "</bug>"


class AnnotFormat(Enum):
    """Class representing kind of bug annotations."""

    SMARTBUGS_FORMAT = "SmartBugs Format"
    SMARTBENCH_FORMAT = "SmartBench Format"
    SOLIDIFI_FORMAT = "SolidiFI Format"


class BugAnnot:
    """Class representing a bug annotation in smart contracts."""

    # Shared index counter for all bug annotations.
    # This counter needs to be reset for each test file.
    index_counter: int = 1

    def __init__(
        self,
        bug_name: str,
        annot_format: AnnotFormat,
        file_path: str,
        start_line: int,
        end_line: int,
    ):
        self.bug_name: str = bug_name
        self.annot_kind: IssueKind = self.map_bug_annot_to_kind(
            bug_name, annot_format
        )
        self.annot_format: AnnotFormat = annot_format
        self.file_path: str = file_path
        self.start_line: int = start_line
        self.end_line: int = end_line
        self.sbc: Optional[SBC] = classify_bug_annot_to_sbc(bug_name)

        # Assign an index to the issue. This index is unique for all issues in
        # the same contract
        self.index = BugAnnot.index_counter
        BugAnnot.index_counter += 1

    def print_concise(self) -> str:
        """Print bug annotation in concise format."""
        location = f"{os.path.basename(self.file_path)}:{self.start_line}"
        if self.start_line != self.end_line:
            location = location + "-" + str(self.end_line)
        return f"Bug ({self.index}): {self.bug_name} - {location}"

    def map_bug_annot_to_kind(self, bug_name: str, annot_format: AnnotFormat):
        """classify bug string in annotation to standard smartbench IssueKind and use annot_format"""
        # TODO: add more bug types for different benchmarks here
        if bug_name in ["FRONT_RUNNING", "TRANSACTION_ORDER_DEPENDENCY"]:
            return IssueKind.TRANSACTION_ORDER_DEPENDENCY
        if bug_name == "ACCESS_CONTROL":
            return IssueKind.ACCESS_CONTROL
        if bug_name in ["ARITHMETIC_BUG", "ARITHMETIC"]:
            return IssueKind.INTEGER_BUG
        if bug_name in ["LEAKING_ETHER", "UNCHECKED_SEND"]:
            return IssueKind.LEAKING_ETHER
        if bug_name == "LOCKING_ETHER":
            return IssueKind.LOCKING_ETHER
        if bug_name == "REENTRANCY":
            return IssueKind.REENTRANCY
        if bug_name == "ASSERTION_FAILURE":
            return IssueKind.ASSERTION_FAILURE
        if bug_name in [
            "BLOCK_DEPENDENCY",
            "TIME_MANIPULATION",
            "BAD_RANDOMNESS",
        ]:
            return IssueKind.BLOCK_VALUE_DEPENDENCY
        if bug_name == ["UNHANDLED_EXCEPTION", "UNCHECKED_LL_CALLS"]:
            return IssueKind.UNHANDLED_EXCEPTION
        if bug_name == "ADDRESS_VALIDATION":
            return IssueKind.LACK_OF_ZERO_ADDRESS_VALIDATION
        if bug_name in ["UNPROTECTED_SELFDESTRUCT", "UNSAFE_SELFDESTRUCT"]:
            return IssueKind.UNSAFE_SELFDESTRUCT
        if bug_name in ["TX_ORIGIN_USAGE", "tx.origin"]:
            return IssueKind.TX_ORIGIN_USAGE
        if bug_name == "UNSAFE_DELEGATECALL":
            return IssueKind.UNSAFE_DELEGATECALL
        # March 29: Add SOLIDIFI
        if bug_name == "Overflow-Underflow":
            return IssueKind.INTEGER_BUG
        if bug_name == "Unchecked-Send":
            return IssueKind.LEAKING_ETHER
        if bug_name == "Unhandled-Exceptions":
            return IssueKind.UNHANDLED_EXCEPTION
        if bug_name == "Re-erntrancy":
            return IssueKind.REENTRANCY
        if bug_name == "tx.origin":
            return IssueKind.TX_ORIGIN_USAGE
        if bug_name == "Timestamp-Dependency":
            return IssueKind.BLOCK_VALUE_DEPENDENCY

    def __str__(self):
        return self.print_concise()


def classify_bug_annot_to_sbc(
    bug_name: str,
) -> Optional[SBC]:
    """Function to classify bug annotation into SmartBug classification SBC."""
    if bug_name == "ACCESS_CONTROL":
        return SBC.ACCESS_CONTROL

    if bug_name == "ARITHMETIC":
        return SBC.ARITHMETIC

    if bug_name == "BAD_RANDOMNESS":
        return SBC.BAD_RANDOMNESS

    if bug_name == "DENIAL_OF_SERVICE":
        return SBC.DENIAL_OF_SERVICE

    if bug_name == "FRONT_RUNNING":
        return SBC.FRONT_RUNNING

    if bug_name == "REENTRANCY":
        return SBC.REENTRANCY

    if bug_name == "SHORT_ADDRESSES":
        return SBC.SHORT_ADDRESSES

    if bug_name == "TIME_MANIPULATION":
        return SBC.TIME_MANIPULATION

    if bug_name == "UNCHECKED_LL_CALLS":
        return SBC.UNCHECKED_LOW_LEVEL_CALLS

    # Unable to match to a SmartBug issue kind
    return None


def parse_smartbugs_annotations(filename: str) -> List[BugAnnot]:
    """Parse bug annotations written in `SmartBugs` format in a smart contract.

    `SmartBugs` format: // <yes/no> <report> <bug type>

    Note: this annotation format can be imprecise if there multiple
    consecutive lines specifying the bug, then the line number of the
    first bug might not be correctly decided.

    In the following example, line number of the first 2 bugs can be
    difficult to determined:

    # ```solidity
    # // <yes> <report> <bug1>
    # // <yes> <report> <bug2>
    # // <yes> <report> <bug3>
    # ... some Solidity source code
    # ```
    """
    bug_annots = []
    with open(filename, "r", encoding="utf-8") as file:
        for index, line in enumerate(file.readlines()):
            start_line = index + 1
            end_line = index + 2
            line = line.strip()
            if (
                line.startswith(COMMENT_TAG)
                and YES_TAG in line
                and REPORT_TAG in line
            ):
                bug_info = line.replace(COMMENT_TAG, "")
                bug_info = bug_info.replace(YES_TAG, "")
                bug_info = bug_info.replace(REPORT_TAG, "")
                for bug_type in bug_info.split(","):
                    bug_annotation = BugAnnot(
                        bug_type.strip(),
                        AnnotFormat.SMARTBUGS_FORMAT,
                        filename,
                        start_line,
                        end_line,
                    )
                    bug_annots.append(bug_annotation)
    return bug_annots


def parse_smartbench_annotations(filename: str) -> List[BugAnnot]:
    """Parse bug annotations written in `SmartBench` format in a smart contract.

    SmartBench format is in HTML-like format.
    // <bug type='bug-type' severity='high'>
    ...
    // </bug>
    """
    warnings.warn("TODO: implement `parse_smartbench_annotations`")
    return []


def parse_solidifi_annotations(filename: str) -> List[BugAnnot]:
    """Parse bug annotations written in `Solidifi` format benchmark."""
    dir_name = os.path.dirname(filename)
    file_name = os.path.basename(filename)
    file_index = int("".join(filter(str.isdigit, file_name)))
    # format buggy_48.sol, only 1 number
    # format annotation BugLog_48.csv
    annotation_file = os.path.join(dir_name, f"BugLog_{file_index}.csv")
    # Read the injected bug logs
    bug_annots = []
    with open(annotation_file, "r") as f:
        reader = csv.reader(f)
        bug_log_list = list(reader)
        for ibug in bug_log_list[1 : len(bug_log_list)]:
            bug_annotation = BugAnnot(
                ibug[2].strip(),
                AnnotFormat.SOLIDIFI_FORMAT,
                filename,
                int(ibug[0]),
                int(ibug[0]) + int(ibug[1]),
            )
            bug_annots.append(bug_annotation)
    return bug_annots


def guess_annotation_type(filename: str) -> Optional[str]:
    """Guess bug format and parse bug annotations."""
    has_smartbugs_annots = False
    has_smartbench_annots = False

    with open(filename, "r", encoding="utf-8") as file:
        for line in file.readlines():
            if BUG_OPEN_TAG in line:
                has_smartbench_annots = True

            if REPORT_TAG in line:
                has_smartbugs_annots = True

    if has_smartbench_annots and (not has_smartbugs_annots):
        return "smartbench"

    if has_smartbugs_annots and (not has_smartbench_annots):
        return "smartbugs"

    if has_smartbugs_annots and has_smartbench_annots:
        warning(
            f"Conflict annotations!"
            f"Found both SmartBench and SmartBugs annotations in: {filename}"
        )
        return None

    # No annotation formats are found
    warning("Unable to guess annotation format!")
    return None


def parse_bug_annotations(test_file: str, annot_format=None) -> List[BugAnnot]:
    """Parse bug annotation in a smart contract.

    The input `annot_format` can take value `smartbugs`, `smartbench`, `solidifi`, or None.
    """
    annot_format = (
        annot_format
        if annot_format is not None
        else guess_annotation_type(test_file)
    )

    if annot_format is None:
        return []

    # Reset bug annotation counter
    BugAnnot.index_counter = 1

    if annot_format.lower() == "smartbugs":
        return parse_smartbugs_annotations(test_file)

    if annot_format.lower() == "smartbench":
        return parse_smartbench_annotations(test_file)

    if annot_format.lower() == "solidifi":
        return parse_solidifi_annotations(test_file)

    warnings.warn("Unknown bug annotation formmat:", annot_format)
    return []


def collect_bug_annotations(test_files: List[str]) -> List[BugAnnot]:
    """Parsing bug annotations from test files"""
    safe_print("\nParsing bug annotations...\n")

    bug_annots = []

    for test_file in test_files:
        safe_print("- Test file: " + test_file)
        annots = parse_bug_annotations(test_file)

        if len(annots) == 0:
            safe_print("  No bug annotations are found!")
            continue

        for annot in annots:
            safe_print(f"  {annot.print_concise()}")

        bug_annots += annots

        safe_print("")

    return bug_annots
