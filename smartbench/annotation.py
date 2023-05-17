#!/usr/bin/env python3

"Module representing a bug annotation."

# Standard Library
import csv
import os
import warnings

from enum import Enum
from typing import List, Optional

# Library
from smartbench import issue
from smartbench.bugdb.sbc import SmartBugsPP
from smartbench.bugdb.sdc import SolidiFIPP
from smartbench.bugdb.smartbench import SmartbenchKind
from smartbench.bugdb.verismart import VeriSmartKind
from smartbench.issue import IssueKind
from smartbench.printer import debug, safe_print, warning


# SmartBugs annotations
YES_TAG = "<yes>"
NO_TAG = "<no>"
REPORT_TAG = "<report>"
COMMENT_TAG = "//"

# SmartBench annotations
BUG_OPEN_TAG = "<bug "
BUG_CLOSE_TAG = "</bug>"

# Verismart annotation
INTEGER_OVERFLOW_TAG = "<INTEGER_OVERFLOW>"
INTEGER_UNDERFLOW_TAG = "<INTEGER_UNDERFLOW>"
LEAKING_VUL_TAG = "<LEAKING_VUL>"
SUICIDAL_VUL_TAG = "<SUICIDAL_VUL>"

class AnnotFormat(Enum):
    """Class representing kind of bug annotations."""

    SMARTBUGS = "SmartBugs"
    SMARTBENCH = "SmartBench"
    SOLIDIFI = "SolidiFI"
    VERISMART = "VeriSmart"


def parse_annot_format_kind(annot_format: str) -> Optional[AnnotFormat]:
    if annot_format.lower() == "smartbugs":
        return AnnotFormat.SMARTBUGS
    elif annot_format.lower() == "smartbench":
        return AnnotFormat.SMARTBENCH
    elif annot_format.lower() == "solidifi":
        return AnnotFormat.SOLIDIFI
    elif annot_format.lower() == "verismart":
        return AnnotFormat.VERISMART
    else:
        return None


class BugAnnot:
    """Class representing a bug annotation in smart contracts."""

    # Shared index counter for all bug annotations.
    # This counter needs to be reset for each test file.
    index_counter: int = 1

    def __init__(
        self,
        annot_name: str,
        is_real_bug: bool,
        annot_format: AnnotFormat,
        file_path: str,
        start_line: int,
        end_line: int,
    ):
        self.annot_name: str = annot_name
        self.is_real_bug: bool = bool(is_real_bug)
        self.annot_format: AnnotFormat = annot_format
        self.file_path: str = file_path
        self.start_line: int = start_line
        self.end_line: int = end_line

        # Classifying this bug annotation to SmartBugs classification
        self.smartbugs_kind: Optional[
            SmartBugsPP
        ] = classify_bug_annot_to_smartbugs_pp_kind(self.annot_name)

        # Classifying this bug annotation to Solidifi classification
        self.solidifi_kind: Optional[
            SolidiFIPP
        ] = classify_bug_annot_to_solidifi_pp_kind(self.annot_name)

        # Classifying this bug annotation to Smartbench classification
        self.smartbench_kind: Optional[
            SmartbenchKind
        ] = classify_bug_annot_to_smartbench_kind(self.annot_name)

        # Classifying this bug annotation to VeriSmart classification
        self.verismart_kind: Optional[
            VeriSmartKind
        ] = classify_bug_annot_to_verismart_kind(self.annot_name)

        # Assign an index to the issue. This index is unique for all issues in
        # the same contract
        self.index = BugAnnot.index_counter
        BugAnnot.index_counter += 1

    def print_concise(self) -> str:
        """Print bug annotation in concise format."""

        annot_type = "Bug" if self.is_real_bug else "NoBug"

        location = f"{os.path.basename(self.file_path)}:{self.start_line}"
        if self.start_line != self.end_line:
            location = location + "-" + str(self.end_line)

        return f"{annot_type} ({self.index}): {self.annot_name} - {location}"

    def map_bug_annot_to_issue_kind(
        self, annot_name: str, annot_format: AnnotFormat
    ) -> Optional[IssueKind]:
        """Classify bug annotation string to issue kind."""

        if annot_format == AnnotFormat.SMARTBUGS:
            return self.map_smartbugs_annot_to_issue_kind(annot_name)
        elif annot_format == AnnotFormat.SOLIDIFI:
            return self.map_solidifi_bug_annot_to_issue_kind(annot_name)
        else:
            warning(f"Unknown bug annotation format: {annot_format}")
            return None

    def map_smartbugs_annot_to_issue_kind(
        self, annot_name: str
    ) -> Optional[IssueKind]:
        """Classify bug annotation string in SmartBugs++ format to issue kind."""

        if annot_name in "FRONT_RUNNING":
            return IssueKind.FRONT_RUNNING

        if annot_name in ["TRANSACTION_ORDER_DEPENDENCY"]:
            return IssueKind.TRANSACTION_ORDER_DEPENDENCY

        if annot_name in ["ACCESS_CONTROL"]:
            return IssueKind.ACCESS_CONTROL

        if annot_name in ["ARITHMETIC"]:
            return IssueKind.INTEGER_BUG

        if annot_name in ["DENIAL_OF_SERVICE"]:
            return IssueKind.DENIAL_OF_SERVICE

        if annot_name in ["LEAKING_ETHER", "UNCHECKED_SEND"]:
            return IssueKind.LEAKING_ETHER

        if annot_name in ["LOCKING_ETHER"]:
            return IssueKind.LOCKING_ETHER

        if annot_name in ["REENTRANCY"]:
            return IssueKind.REENTRANCY

        if annot_name in ["ASSERTION_FAILURE"]:
            return IssueKind.ASSERTION_FAILURE

        if annot_name in ["BLOCK_DEPENDENCY"]:
            return IssueKind.BLOCK_VALUE_DEPENDENCY

        if annot_name in ["UNHANDLED_EXCEPTION"]:
            return IssueKind.UNHANDLED_EXCEPTION

        if annot_name in ["UNCHECKED_LL_CALLS"]:
            return IssueKind.UNCHECKED_LOW_LEVEL_CALLS

        if annot_name in ["ADDRESS_VALIDATION"]:
            return IssueKind.LACK_OF_ZERO_ADDRESS_VALIDATION

        if annot_name in [
            "UNPROTECTED_SELFDESTRUCT",
            "UNSAFE_SELFDESTRUCT",
        ]:
            return IssueKind.UNSAFE_SELFDESTRUCT

        if annot_name in ["TX_ORIGIN_USAGE", "tx.origin"]:
            return IssueKind.AUTHORIZATION_THROUGH_TX_ORIGIN

        if annot_name in ["UNSAFE_DELEGATECALL"]:
            return IssueKind.UNSAFE_DELEGATECALL

        return None

    def map_solidifi_bug_annot_to_issue_kind(
        self, annot_name: str
    ) -> Optional[IssueKind]:
        """Classify bug annotation string in Solidifi++ format to issue kind."""

        if annot_name in ["Overflow-Underflow"]:
            return IssueKind.INTEGER_BUG

        if annot_name in ["Unchecked-Send"]:
            return IssueKind.LEAKING_ETHER

        if annot_name in ["Unhandled-Exceptions"]:
            return IssueKind.UNHANDLED_EXCEPTION

        if annot_name in ["Re-erntrancy"]:
            return IssueKind.REENTRANCY

        if annot_name in ["tx.origin"]:
            return IssueKind.AUTHORIZATION_THROUGH_TX_ORIGIN

        if annot_name in ["Timestamp-Dependency"]:
            return IssueKind.BLOCK_VALUE_DEPENDENCY

        return None

    def __str__(self):
        return self.print_concise()


def classify_bug_annot_to_smartbugs_pp_kind(
    annot_name: str,
) -> Optional[SmartBugsPP]:
    """Classify bug annotation string in SmartBugs++ format to issue kind."""

    # SmartBugs annotations
    if annot_name in ["ACCESS_CONTROL"]:
        return SmartBugsPP.ACCESS_CONTROL

    if annot_name in ["ASSERTION_FAILURE"]:
        return SmartBugsPP.ASSERTION_FAILURE

    if annot_name in ["ARITHMETIC"]:
        return SmartBugsPP.ARITHMETIC

    if annot_name in ["BLOCK_DEPENDENCY"]:
        return SmartBugsPP.BLOCK_DEPENDENCY

    if annot_name in ["DENIAL_OF_SERVICE"]:
        return SmartBugsPP.DENIAL_OF_SERVICE

    if annot_name in "FRONT_RUNNING":
        return SmartBugsPP.FRONT_RUNNING

    if annot_name in ["LEAKING_ETHER"]:
        return SmartBugsPP.LEAKING_ETHER

    if annot_name in ["LOCKING_ETHER"]:
        return SmartBugsPP.LOCKING_ETHER

    if annot_name in ["REENTRANCY"]:
        return SmartBugsPP.REENTRANCY

    if annot_name in ["SHORT_ADDRESSES"]:
        return SmartBugsPP.SHORT_ADDRESSES

    if annot_name in ["TRANSACTION_ORDER_DEPENDENCY"]:
        return SmartBugsPP.TRANSACTION_ORDER_DEPENDENCY

    if annot_name in ["UNCHECKED_LL_CALLS", "UNHANDLED_EXCEPTION"]:
        return SmartBugsPP.UNHANDLED_EXCEPTION

    if annot_name in ["UNPROTECTED_SELFDESTRUCT"]:
        return SmartBugsPP.UNPROTECTED_SELFDESTRUCT

    return None


def classify_bug_annot_to_solidifi_pp_kind(
    annot_name: str,
) -> Optional[SolidiFIPP]:
    """Classify bug annotation string in SolidiFI format to issue kind."""
    # SolidiFI annotations
    if annot_name == "Overflow-Underflow":
        return SolidiFIPP.OVERFLOW_UNDERFLOW

    if annot_name == "Re-entrancy":
        return SolidiFIPP.REENTRANCY

    if annot_name == "Timestamp-Dependency":
        return SolidiFIPP.TIMESTAMP_DEPENDENCY

    if annot_name == "Unchecked-Send":
        return SolidiFIPP.UNCHECKED_SEND

    if annot_name == "Unhandled-Exceptions":
        return SolidiFIPP.UNHANDLED_EXCEPTION

    if annot_name == "tx.origin":
        return SolidiFIPP.TX_ORIGIN

    return None


def classify_bug_annot_to_smartbench_kind(
    annot_name: str,
) -> Optional[SmartbenchKind]:
    """Classify bug annotation string in Smartbench format to issue kind."""

    # Smartbench annotations
    if annot_name in ["ACCESS_CONTROL"]:
        return SmartbenchKind.ACCESS_CONTROL

    if annot_name in ["REENTRANCY"]:
        return SmartbenchKind.REENTRANCY

    return None

def classify_bug_annot_to_verismart_kind(
    annot_name: str,
) -> Optional[VeriSmartKind]:
    """Classify bug annotation string in VeriSmart format to issue kind."""

    # VeriSmart annotations
    if annot_name in ["ARITHMETIC"]:
        return VeriSmartKind.ARITHMETIC

    if annot_name in ["LEAKING_ETHER"]:
        return VeriSmartKind.LEAKING_ETHER

    if annot_name in ["UNSAFE_SELFDESTRUCT"]:
        return VeriSmartKind.UNSAFE_SELFDESTRUCT

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
            start_line = end_line = index + 2
            line = line.strip()
            if (
                line.startswith(COMMENT_TAG)
                and (YES_TAG in line or NO_TAG in line)
                and REPORT_TAG in line
            ):
                is_real_bug = YES_TAG in line
                bug_types = line.replace(COMMENT_TAG, "")
                bug_types = bug_types.replace(YES_TAG, "")
                bug_types = bug_types.replace(NO_TAG, "")
                bug_types = bug_types.replace(REPORT_TAG, "")
                for bug_type in bug_types.split(","):
                    bug_annotation = BugAnnot(
                        bug_type.strip(),
                        is_real_bug,
                        AnnotFormat.SMARTBUGS,
                        filename,
                        start_line,
                        end_line,
                    )
                    bug_annots.append(bug_annotation)
    return bug_annots

def parse_verismart_annotations(filename: str) -> List[BugAnnot]:
    """Parse bug annotations written in `VeriSmart` format in a smart contract.

    `VeriSmart` format: // <bug type>
    """
    bug_annots = []
    with open(filename, "r", encoding="utf-8") as file:
        for index, line in enumerate(file.readlines()):
            start_line = end_line = index + 1
            line = line.strip()
            if (COMMENT_TAG in line):
                bug_types = []

                if INTEGER_OVERFLOW_TAG in line or INTEGER_UNDERFLOW_TAG in line:
                    bug_type = "ARITHMETIC"
                    bug_types.append(bug_type)

                if LEAKING_VUL_TAG in line:
                    bug_type = "LEAKING_ETHER"
                    bug_types.append(bug_type)

                if SUICIDAL_VUL_TAG in line:
                    bug_type = "UNSAFE_SELFDESTRUCT"
                    bug_types.append(bug_type)


                if bug_types != []:
                    for bug_type in bug_types:
                        bug_annotation = BugAnnot(
                            bug_type,
                            True,
                            AnnotFormat.VERISMART,
                            filename,
                            start_line,
                            end_line,
                        )
                        bug_annots.append(bug_annotation)
    return bug_annots


def parse_smartbench_annotations(filename: str) -> List[BugAnnot]:
    """Parse bug annotations written in `SmartBench` format in a smart contract.

    SmartBench format is in HTML-like format.
    // <bug BUG_TYPE>
    ...
    // </bug>
    """

    bug_annots = []
    with open(filename, "r", encoding="utf-8") as file:
        bug_type = None
        start_line = None
        for index, line in enumerate(file.readlines()):
            line = line.strip()
            if (
                line.startswith(COMMENT_TAG)
                and BUG_OPEN_TAG in line
            ):
                start_line = index + 1
                bug_type = line.replace(COMMENT_TAG, "")
                bug_type = bug_type.replace(BUG_OPEN_TAG, "")
                bug_type = bug_type.strip()
                # Remove the ">" character at the end
                bug_type = bug_type[:-1]

            if (
                line.startswith(COMMENT_TAG)
                and BUG_CLOSE_TAG in line
            ):
                if bug_type is not None and start_line is not None:
                    end_line = index + 1
                    bug_annotation = BugAnnot(
                        bug_type,
                        True,
                        AnnotFormat.SMARTBENCH,
                        filename,
                        start_line,
                        end_line,
                    )
                    bug_annots.append(bug_annotation)
                    bug_type = None
                    start_line = None

    return bug_annots


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
                True,
                AnnotFormat.SOLIDIFI,
                filename,
                int(ibug[0]),
                int(ibug[0]) + int(ibug[1]) - 1,
            )
            bug_annots.append(bug_annotation)
    return bug_annots


def guess_annotation_type(filename: str) -> Optional[AnnotFormat]:
    """Guess bug format and parse bug annotations."""
    has_smartbugs_annots = False
    has_smartbench_annots = False
    has_verismart_annots = False

    with open(filename, "r", encoding="utf-8") as file:
        for line in file.readlines():
            if BUG_OPEN_TAG in line:
                has_smartbench_annots = True

            if REPORT_TAG in line:
                has_smartbugs_annots = True

            if (INTEGER_OVERFLOW_TAG in line or INTEGER_UNDERFLOW_TAG in line or
                LEAKING_VUL_TAG in line or SUICIDAL_VUL_TAG in line):
                has_verismart_annots = True

    if has_smartbench_annots and (not has_smartbugs_annots):
        return AnnotFormat.SMARTBENCH

    if has_smartbugs_annots and (not has_smartbench_annots):
        return AnnotFormat.SMARTBUGS

    if has_verismart_annots:
        return AnnotFormat.VERISMART

    if has_smartbugs_annots and has_smartbench_annots:
        warning(
            f"Conflict annotations!"
            f"Found both SmartBench and SmartBugs annotations in: {filename}"
        )
        return None

    # No annotation formats are found
    debug("Unable to guess annotation format!")
    return None


def parse_bug_annotations(
    test_file: str, annot_format: Optional[AnnotFormat] = None
) -> List[BugAnnot]:
    """Parse bug annotation in a smart contract.

    The input `annot_format` can take value `smartbugs`, `smartbench`,
    `solidifi`, `verismart` or None.
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

    if annot_format == AnnotFormat.SMARTBUGS:
        return parse_smartbugs_annotations(test_file)

    if annot_format == AnnotFormat.SMARTBENCH:
        return parse_smartbench_annotations(test_file)

    if annot_format == AnnotFormat.SOLIDIFI:
        return parse_solidifi_annotations(test_file)

    if annot_format == AnnotFormat.VERISMART:
        return parse_verismart_annotations(test_file)

    debug(f"Unknown bug annot formmat: {annot_format}\n")
    return []


def parse_bug_annotations_all_files(
    test_files: List[str], annot_format: Optional[AnnotFormat] = None
) -> List[BugAnnot]:
    """Parsing bug annotations from test files"""
    safe_print("\nParsing bug annotations...\n")

    bug_annots = []

    for test_file in test_files:
        safe_print("Test file: " + test_file)
        annots = parse_bug_annotations(test_file, annot_format)

        if len(annots) == 0:
            safe_print("- No bug annotations!\n")
            continue

        for annot in annots:
            safe_print(f"- {annot.print_concise()}")

        bug_annots += annots

        safe_print("")

    return bug_annots
