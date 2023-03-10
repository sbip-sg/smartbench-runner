#!/usr/bin/env python3

# Standard Library
import sys
import warnings

from typing import List

# Library
from smartbench.debug import warning


# SmartBugs labels
YES_TAG = "<yes>"
NO_TAG = "<no>"
REPORT_TAG = "<report>"
COMMENT_TAG = "//"

# SmartBench labels
BUG_OPEN_TAG = "<bug "
BUG_CLOSE_TAG = "</bug>"


class BugLabel:
    """Class representing a bug label in smart contracts."""

    def __init__(self, filename, start_line, end_line, bug_category):
        self.filename = filename
        self.start_line = start_line
        self.end_line = end_line
        self.bug_category = bug_category


# Bug line number in SmartBug format can be imprecise: if there are two
# consecutive lines specifying the bug, then the line number of
# the first bug might not be correctly decided.
#
# ```solidity
# // <yes> <report> <bug1>
# // <yes> <report> <bug2>
# // <yes> <report> <bug3>
# ... some Solidity source code
# ```
def parse_smartbugs_labels(filename: str) -> List[BugLabel]:
    """Parse bug labels written in SmartBugs format in a smart contract.

    SmartBugs format: // <yes/no> <report> <bug type>
    """
    bug_labels = []
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
                bug_category = line.replace(COMMENT_TAG, "")
                bug_category = bug_category.replace(YES_TAG, "")
                bug_category = bug_category.replace(REPORT_TAG, "")
                bug_category = bug_category.strip()
                bug_label = BugLabel(
                    filename, start_line, end_line, bug_category
                )
                bug_labels.append(bug_label)
    return bug_labels


def parse_smartbench_labels(filename: str) -> List[BugLabel]:
    """Parse bug labels written in SmartBench format in a smart contract.

    SmartBench format is in HTML-like format.
    // <bug type='bug-type' severity='high'>
    ...
    // </bug>
    """
    warnings.warn("TODO: implement `parse_smartbench_labels`")
    return []


def guess_and_parse_labels(filename: str) -> List[BugLabel]:
    """Guess bug format and parse bug labels."""
    has_smartbugs_labels = False
    has_smartbench_labels = False

    with open(filename, "r", encoding="utf-8") as file:
        for line in file.readlines():
            if BUG_OPEN_TAG in line:
                has_smartbench_labels = True

            if REPORT_TAG in line:
                has_smartbugs_labels = True

    if has_smartbench_labels and (not has_smartbugs_labels):
        return parse_smartbench_labels(filename)

    if has_smartbugs_labels and (not has_smartbench_labels):
        return parse_smartbugs_labels(filename)

    if has_smartbugs_labels and has_smartbench_labels:
        warning(
            "Found both SmartBench and SmartBugs label format in file:",
            filename,
        )
        warning("Quit parsing labels...")
        return []

    # No label formats are found
    return []


def parse_bug_labels(filename: str, label_format=None) -> List[BugLabel]:
    """Parse bug labels from a smart contracts.

    Bug label format can be `smartbugs`, `smartbench`, or `auto` formats.
    """
    if label_format is None:
        return guess_and_parse_labels(filename)

    if label_format.lower() == "smartbugs":
        return parse_smartbugs_labels(filename)

    if label_format.lower() == "smartbench":
        return parse_smartbench_labels(filename)

    warnings.warn("Invalid bug formmat:", label_format)
    return []
