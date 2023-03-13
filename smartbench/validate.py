#!/usr/bin/env python3

"""Module to validate analysis results with bug annotations."""

# Standard Library
from enum import Enum
from typing import List, Union

# Library
from smartbench import bug_annot
from smartbench.bug_annot import BugAnnot
from smartbench.issue import Issue
from smartbench.tools.tool import Tool


class IssueStatus(Enum):
    """Class representing status of a reported issue."""

    TRUE_POSITIVE = "True Positive"
    TRUE_NEGATIVE = "True Negative"
    FALSE_POSITIVE = "False Positive"
    INVALIDATED = "Invalidated"


class Validation:
    """Class capturing the validation result between detected issues and
    bug annotations in a smart contract."""

    # Attributes
    test_file: str
    tool: Tool
    true_positives: List[Issue]  # List of bugs that are correctly reported.
    true_negatives: List[Issue]  # List of bugs that are not reported.
    false_positives: List[Issue]  # List of wrong issues that are reported.
    invalidated: List[Issue]  # Issues that do not belong to the above list


def validate_issue(issue: Issue, annots: List[BugAnnot]) -> IssueStatus:
    """Validate analysis results with bug annotations."""
    issue.smartbug_classification
    for annot in annots:
        pass


def validate_detected_issues(
    tool: Tool, test_file: str, issues: List[Issue]
) -> Union[Validation, None]:
    """Validate detected issues against bug annotations in an input file."""
    annots = bug_annot.parse_bug_annotations(test_file)
    pass
