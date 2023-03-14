#!/usr/bin/env python3

"""Module to validate analysis results with bug annotations."""

# Standard Library
from dataclasses import dataclass
from enum import Enum
from typing import List

# Library
from smartbench import bug_annot
from smartbench.bug_annot import AnnotFormat, BugAnnot
from smartbench.bugdb.smartbugs import SmartBugsKind
from smartbench.issue import Issue
from smartbench.location import Location


class IssueStatus(Enum):
    """Class representing status of a reported issue."""

    TRUE_POSITIVE = "True Positive"
    FALSE_POSITIVE = "False Positive"
    UNKNOWN = "Unknown"


@dataclass
class Validation:
    """Class capturing the validation result between detected issues and
    bug annotations in a smart contract."""

    # Attributes
    test_file: str
    issues: List[Issue]  # All reported issues that are validated.
    bug_annotations: List[BugAnnot]  # All bug annotations considered.
    correct_issues: List[Issue]  # Issues that are reported.
    incorrect_issues: List[Issue]  # Issues that are reported incorrectly.
    unknown_issues: List[Issue]  # Issues unrelated to bug annotations.
    missing_bugs: List[BugAnnot]  # Bug annotations that are not reported.


def match_issue_to_annotation(issue: Issue, annot: BugAnnot) -> bool:
    """Function to check whether an reported issue is related to a bug
    annotation."""
    # Check whether the issue kind and bug annotation kind are related
    if annot.annot_format == AnnotFormat.SMARTBUGS_FORMAT:
        if annot.smatbugs_kind != annot.smatbugs_kind:
            return False
    elif annot.annot_format == AnnotFormat.SMARTBENCH_FORMAT:
        # TODO: implement later
        return False
    else:
        return False

    # Check whether the issue and bug annotation are of the same file.
    iloc: Location = issue.location
    if iloc.file_path != annot.file_path:
        return False

    # Check whether the issue location is covered by the annotation location.
    if iloc.start_line is not None and iloc.start_line < annot.start_line:
        return False
    if iloc.end_line is not None and iloc.end_line > annot.end_line:
        return False

    # Pass all criteria to match an issue with a bug annotation
    return True


def validate_issues(test_file: str, issues: List[Issue]) -> Validation:
    """Validate detected issues against bug annotations in an input file."""
    correct_issues: List[Issue] = []
    incorrect_issues: List[Issue] = []
    unknown_issues: List[Issue] = []

    annots = bug_annot.parse_bug_annotations(test_file)
    reported_annots: List[BugAnnot] = []

    checked_smartbugs_kinds = []
    if any(a.annot_format == AnnotFormat.SMARTBUGS_FORMAT for a in annots):
        checked_smartbugs_kinds = SmartBugsKind.elements()

    for issue in issues:
        # True-positive issue
        correct_bug = False
        for annot in annots:
            if match_issue_to_annotation(issue, annot):
                correct_issues.append(issue)
                reported_annots.append(annot)
                correct_bug = True
                break

        # False-positive issue
        if not correct_bug and issue.smartbugs_kind in checked_smartbugs_kinds:
            incorrect_issues.append(issue)

        # Unknown issue
        else:
            unknown_issues.append(issue)

    # Missing bugs:
    missing_bugs = [b for b in annots if b not in reported_annots]

    return Validation(
        test_file,
        issues,
        annots,
        correct_issues,
        incorrect_issues,
        unknown_issues,
        missing_bugs,
    )
