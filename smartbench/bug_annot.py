#!/usr/bin/env python3

"Module representing a bug annotation."

# Standard Library
import warnings

from enum import Enum
from typing import List, Union

# Library
from smartbench.bugdb.smartbugs import SmartBugsKind
from smartbench.debug import warning


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


class BugAnnot:
    """Class representing a bug annotation in smart contracts."""

    bug_name: str  # Bug info as annotated in source code.
    annot_format: AnnotFormat
    file_name: str
    start_line: int
    end_line: int
    smatbugs_kind: Union[SmartBugsKind, None]

    def __init__(self, bug_name, annot_format, filename, start_line, end_line):
        self.bug_name = bug_name
        self.annot_format = annot_format
        self.filename = filename
        self.start_line = start_line
        self.end_line = end_line
        self.smatbugs_kind = classify_bug_annot_to_smartbugs_kind(bug_name)

    def print_by_line(self) -> str:
        res = f"Line {self.start_line}"
        if self.start_line != self.end_line:
            res = res + "-" + str(self.end_line)
        res = res + ": " + self.bug_name
        return res


def classify_bug_annot_to_smartbugs_kind(
    bug_name: str,
) -> Union[SmartBugsKind, None]:
    """Function to classify bug annotation in SmartBug format."""
    if bug_name == "ACCESS_CONTROL":
        return SmartBugsKind.ACCESS_CONTROL

    if bug_name == "ARITHMETIC":
        return SmartBugsKind.ARITHMETIC

    if bug_name == "BAD_RANDOMNESS":
        return SmartBugsKind.BAD_RANDOMNESS

    if bug_name == "DENIAL_OF_SERVICE":
        return SmartBugsKind.DENIAL_OF_SERVICE

    if bug_name == "FRONT_RUNNING":
        return SmartBugsKind.FRONT_RUNNING

    if bug_name == "REENTRANCY":
        return SmartBugsKind.REENTRANCY

    if bug_name == "SHORT_ADDRESSES":
        return SmartBugsKind.SHORT_ADDRESSES

    if bug_name == "TIME_MANIPULATION":
        return SmartBugsKind.TIME_MANIPULATION

    if bug_name == "UNCHECKED_LL_CALLS":
        return SmartBugsKind.UNCHECKED_LOW_LEVEL_CALLS

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
            end_line = index + 1
            line = line.strip()
            if (
                line.startswith(COMMENT_TAG)
                and YES_TAG in line
                and REPORT_TAG in line
            ):
                bug_type = line.replace(COMMENT_TAG, "")
                bug_type = bug_type.replace(YES_TAG, "")
                bug_type = bug_type.replace(REPORT_TAG, "")
                bug_type = bug_type.strip()
                bug_annotation = BugAnnot(
                    bug_type,
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


def guess_annotation_type(filename: str) -> Union[str, None]:
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

    The input `annot_format` can take value `smartbugs`, `smartbench`, or None.
    """
    annot_format = (
        annot_format
        if annot_format is not None
        else guess_annotation_type(test_file)
    )

    if annot_format is None:
        return []

    if annot_format.lower() == "smartbugs":
        return parse_smartbugs_annotations(test_file)

    if annot_format.lower() == "smartbench":
        return parse_smartbench_annotations(test_file)

    warnings.warn("Unknown bug annotation formmat:", annot_format)
    return []


def collect_bug_annotations(test_files: List[str]) -> List[BugAnnot]:
    """Parsing bug annotations from test files"""
    print("\nParsing bug annotations...\n")

    bug_annots = []

    for test_file in test_files:
        print("- Test file: " + test_file)
        annots = parse_bug_annotations(test_file)

        if len(annots) == 0:
            print("  No bug annotations are found!")
            continue

        for annot in annots:
            print(f"  {annot.print_by_line()}")

        bug_annots += annots

        print("")

    return bug_annots
