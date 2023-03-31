#!/usr/bin/env python3

"""Module to validate analysis results with bug annotations."""

# Standard Library
from dataclasses import dataclass
from enum import Enum
from typing import List

# Library
from smartbench import bug_annot, issue, result
from smartbench.bug_annot import AnnotFormat, BugAnnot
from smartbench.bugdb.sbc import SBC
from smartbench.issue import Issue
from smartbench.loc import Location
from smartbench.tools.slither import slither
from smartbench.tools.mythril import mythril
from smartbench.tools.sfuzz import sfuzz
from smartbench.tools.sfuzz.sfuzz import Sfuzz
from smartbench.tools.slither.slither import Slither
from smartbench.tools.smartfuzz import smartfuzz
from smartbench.tools.smartian import smartian
from smartbench.tools.confuzzius import confuzzius
from smartbench.tools.confuzzius.confuzzius import Confuzzius
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

    def num_correct_issues(self) -> int:
        return len(self.correct_issues)

    def print_summary(self) -> None:
        print("- Validation:")

        correct_issue_info = f"{len(self.correct_issues)}"
        correct_idxs = [x.index for x in self.correct_issues]
        if len(correct_idxs) > 0:
            correct_issue_info += (
                f" [Issue IDs: {result.print_indices(correct_idxs)}]"
            )
        print(f"  + Correct issues: {correct_issue_info}")

        wrong_issue_info = f"{len(self.incorrect_issues)}"
        wrong_idxs = [x.index for x in self.incorrect_issues]
        if len(wrong_idxs) > 0:
            wrong_issue_info += (
                f" [Issue IDs: {result.print_indices(wrong_idxs)}]"
            )
        print(f"  + Wrong issues: {wrong_issue_info}")

        print(f"  + Unknown issues: {len(self.unknown_issues)}")

        missing_bug_info = f"{len(self.missing_bugs)}"
        missing_idxs = [x.index for x in self.missing_bugs]
        if len(missing_idxs) > 0:
            missing_bug_info += (
                f" [Bug IDs: {result.print_indices(missing_idxs)}]"
            )
        print(f"  + Missing bugs: {missing_bug_info}")


@dataclass
class SolidifiValidationResult:
    test_file: str
    issues: List[Issue]
    bug_annotations: List[BugAnnot]
    correct_bugs: List[BugAnnot]
    missing_bugs: List[BugAnnot]
    unlabelled_issues: List[Issue]

    def num_correct_issues(self) -> int:
        return len(self.correct_bugs)

    def print_summary(self) -> None:
        print("- SOLIDIFI Validation:")
        correct_issue_info = f"{len(self.correct_bugs)}"
        correct_idxs = [x.index for x in self.correct_bugs]
        if len(correct_idxs) > 0:
            correct_issue_info += (
                f" [Issue IDs: {result.print_indices(correct_idxs)}]"
            )
        print(f"  + Correct injected bugs: {correct_issue_info}")
        print(f"  + Unlabelled detected bugs: {len(self.unlabelled_issues)}")
        missing_bug_info = f"{len(self.missing_bugs)}"
        missing_idxs = [x.index for x in self.missing_bugs]
        if len(missing_idxs) > 0:
            missing_bug_info += (
                f" [Bug IDs: {result.print_indices(missing_idxs)}]"
            )
        print(f"  + Missing injected bugs: {missing_bug_info}")


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

    # Check whether the issue and bug annotation are of the same file.
    iloc: Location = issue.location
    # Remove unneccessary path information
    # if iloc.file_path != annot.file_path:
    #     return False

    match_command = None

    if isinstance(tool, Slither):
        tool.match_location_of_issue_to_annotation(issue, annot)

    if isinstance(tool, Sfuzz):
        tool.match_location_of_issue_to_annotation(issue, annot)

    if isinstance(tool, Confuzzius):
        tool.match_location_of_issue_to_annotation(issue, annot)

    if tool.is_mythril():
        match_command = mythril.match_location_of_issue_to_annotation

    if tool.is_smartian():
        match_command = smartian.match_location_of_issue_to_annotation

    if tool.is_smartfuzz():
        match_command = smartfuzz.match_location_of_issue_to_annotation

    if match_command:
        return match_command(issue, annot)

    # Check whether the issue location is covered by the annotation location.
    if iloc.start_line is None or iloc.end_line is None:
        return False
    if iloc.start_line < annot.start_line + 1:
        return False
    if iloc.end_line > annot.end_line - 1:
        return False

    # Pass all criteria to match an issue with a bug annotation
    return True


def validate_issues(
    tool: Tool,
    test_file: str,
    issues: List[Issue],
    annots: List[BugAnnot],
    benchmark_name: str = "",
) -> ValidationResult:
    """Validate detected issues against bug annotations in an input file."""

    # not used in solidifi
    correct_issues: List[Issue] = []
    incorrect_issues: List[Issue] = []
    # solidifi without missclassified bugs.
    unlabelled_issues: List[Issue] = []
    reported_annots: List[BugAnnot] = []
    missing_annots: List[BugAnnot] = []
    if benchmark_name.lower() == "solidifi":
        # special case for solidifi, other benchmarks may copy:
        # two-loop to deal with dupplicated bugs annotation & multiple issues reported the same annotation
        # first loop detect missing bug. Simply checks if any annot is not reported
        for annot in annots:
            # True-positive issues
            detected = False
            for issue in issues:
                if match_issue_to_annotation(tool, issue, annot):
                    detected = True
                    break
            if detected:
                reported_annots.append(annot)
            else:
                missing_annots.append(annot)
        # second loop detect unlabelled_issues
        for issue in issues:
            # True-positive issue
            matched_bug = False
            for annot in annots:
                if match_issue_to_annotation(tool, issue, annot):
                    matched_bug = True
                    break
            # Unknown issue
            if not matched_bug:
                unlabelled_issues.append(issue)
        return SolidifiValidationResult(
            test_file,
            issues,
            annots,
            reported_annots,
            missing_annots,
            unlabelled_issues,
        )

    # target_sbcs = []
    # if any(a.annot_format == AnnotFormat.SMARTBUGS_FORMAT for a in annots):
    #     target_sbcs = SBC.elements()

    for annot in annots:
        # True-positive issue
        # correct_bug = False
        for issue in issues:
            if match_issue_to_annotation(tool, issue, annot):
                correct_issues.append(issue)
                reported_annots.append(annot)
                # correct_bug = True
                break

        # # False-positive issue
        # if not correct_bug and issue.sbc in target_sbcs:
        #     incorrect_issues.append(issue)

        # # Unknown issue
        # else:
        #     unknown_issues.append(issue)

    # Missing bugs:
    missing_bugs = [b for b in annots if b not in reported_annots]
    return ValidationResult(
        test_file,
        issues,
        annots,
        correct_issues,
        incorrect_issues,
        unlabelled_issues,
        missing_bugs,
    )
