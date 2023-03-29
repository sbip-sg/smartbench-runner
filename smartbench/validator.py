#!/usr/bin/env python3

"""Module to validate analysis results with bug annotations."""

# Standard Library
from dataclasses import dataclass
from enum import Enum
from typing import List

# Library
from smartbench import bug_annot, issue
from smartbench.bug_annot import AnnotFormat, BugAnnot
from smartbench.bugdb.sbc import SBC
from smartbench.issue import Issue
from smartbench.location import Location
from smartbench.tools.confuzzius import confuzzius
from smartbench.tools.mythril import mythril
from smartbench.tools.smartian import smartian
from smartbench.tools.tool import Tool


class IssueStatus(Enum):
    """Class representing status of a reported issue."""

    TRUE_POSITIVE = "True Positive"
    FALSE_POSITIVE = "False Positive"
    UNKNOWN = "Unknown"


@dataclass
class ValidationResult:
    """Class capturing the validation result between detected issues and
    bug annotations in a smart contract."""

    def __init__(
        self,
        test_file: str,
        issues: List[Issue],
        bug_annotations: List[BugAnnot],
        correct_issues: List[Issue],
        incorrect_issues: List[Issue],
        unknown_issues: List[Issue],
        missing_bugs: List[BugAnnot],
    ):
        self.test_file = test_file

        # All the issues that are reported
        self.issues: List[Issue] = list(issues)

        # Bug annotations specified for the test files.
        self.bug_annotations: List[BugAnnot] = list(bug_annotations)

        # Issues that are reported.
        self.correct_issues: List[Issue] = list(correct_issues)

        # Issues that are reported incorrectly.
        self.incorrect_issues: List[Issue] = list(incorrect_issues)

        # Issues unrelated to bug annotations.
        self.unknown_issues: List[Issue] = list(unknown_issues)

        # Bug annotations that are not reported.
        self.missing_bugs: List[BugAnnot] = list(missing_bugs)


def match_issue_to_annotation(
    tool: Tool, issue: Issue, annot: BugAnnot
) -> bool:
    """Function to check whether an reported issue is related to a bug
    annotation."""
    # Check whether the issue kind and bug annotation kind are related
    if annot.annot_format == AnnotFormat.SMARTBUGS_FORMAT:
        if annot.sbc != annot.sbc:
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

    match_command = None

    if tool.is_confuzzius():
        match_command = confuzzius.match_location_of_issue_to_annotation

    if tool.is_mythril():
        match_command = mythril.match_location_of_issue_to_annotation

    if tool.is_smartian():
        match_command = smartian.match_location_of_issue_to_annotation

    if match_command:
        return match_command(issue, annot)

    # # Check whether the issue location is covered by the annotation location.
    if iloc.start_line is None or iloc.end_line is None:
        return False
    if iloc.start_line < annot.start_line + 1:
        return False
    if iloc.end_line > annot.end_line + 1:
        return False

    # Pass all criteria to match an issue with a bug annotation
    return True


def validate_issues(
    tool: Tool, test_file: str, issues: List[Issue]
) -> ValidationResult:
    """Validate detected issues against bug annotations in an input file."""

    correct_issues: List[Issue] = []
    incorrect_issues: List[Issue] = []
    unknown_issues: List[Issue] = []

    annots = bug_annot.parse_bug_annotations(test_file)
    reported_annots: List[BugAnnot] = []

    target_sbcs = []
    if any(a.annot_format == AnnotFormat.SMARTBUGS_FORMAT for a in annots):
        target_sbcs = SBC.elements()

    for issue in issues:
        # True-positive issue
        correct_bug = False
        for annot in annots:
            if match_issue_to_annotation(tool, issue, annot):
                correct_issues.append(issue)
                reported_annots.append(annot)
                correct_bug = True
                break

        # False-positive issue
        if not correct_bug and issue.sbc in target_sbcs:
            incorrect_issues.append(issue)

        # Unknown issue
        else:
            unknown_issues.append(issue)

    # Missing bugs:
    missing_bugs = [b for b in annots if b not in reported_annots]

    return ValidationResult(
        test_file,
        issues,
        annots,
        correct_issues,
        incorrect_issues,
        unknown_issues,
        missing_bugs,
    )
