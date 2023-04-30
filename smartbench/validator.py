#!/usr/bin/env python3

"""Module to validate analysis results with bug annotations."""

# Standard Library
from typing import List, Tuple

# Third Party
import more_itertools as mit

# Library
from smartbench.annotation import AnnotFormat, BugAnnot
from smartbench.issue import Issue
from smartbench.printer import debug, safe_print
from smartbench.solidity.loc import Location
from smartbench.tools.tool import Tool


class ValidationResult:
    def __init__(
        self,
        correct_bugs: List[Tuple[Issue, BugAnnot]],
        missing_bugs: List[BugAnnot],
        unlabelled_issues: List[Issue],
    ):
        # Issues that are reported.
        self.correct_bugs: List[(Issue, BugAnnot)] = list(correct_bugs)

        # Bug annotations that are not reported.
        self.missing_bugs: List[BugAnnot] = list(missing_bugs)

        # Issues unrelated to bug annotations.
        self.unlabelled_issues: List[Issue] = list(unlabelled_issues)

    def num_correct_bugs(self) -> int:
        return len(self.correct_bugs)

    def print_summary(self, parallel_mode=False) -> None:
        if not parallel_mode:
            safe_print("- Validation:")

            # Print correct bugs
            correct_bugs_info = f"{len(self.correct_bugs)}"
            correct_issue_idxs = [i.index for (i, _) in self.correct_bugs]
            if len(correct_issue_idxs) > 0:
                correct_bugs_info += (
                    f" [Issue IDs: {print_indices(correct_issue_idxs)}]"
                )
            safe_print(f"  + Correct bugs: {correct_bugs_info}")

            # Print missing bugs
            missing_bug_info = f"{len(self.missing_bugs)}"
            missing_bug_idxs = [b.index for b in self.missing_bugs]
            if len(missing_bug_idxs) > 0:
                missing_bug_info += (
                    f" [Bug annot IDs: {print_indices(missing_bug_idxs)}]"
                )
            safe_print(f"  + Missing bugs: {missing_bug_info}")

            # Print unlabelled issues
            unlabelled_info = f"{len(self.unlabelled_issues)}"
            unlabelled_idxs = [i.index for i in self.unlabelled_issues]
            if len(unlabelled_idxs) > 0:
                unlabelled_info += (
                    f" [Issue IDs: {print_indices(unlabelled_idxs)}]"
                )
            safe_print(f"  + Unlabelled issues: {unlabelled_info}")


def print_indices(indices: List[int]) -> str:
    index_groups = [list(group) for group in mit.consecutive_groups(indices)]
    groups = [
        f"{group[0]}-{group[-1]}" if len(group) > 1 else f"{group[0]}"
        for group in index_groups
    ]
    return ", ".join(groups)


def match_issue_to_annotation(
    tool: Tool, issue: Issue, annot: BugAnnot
) -> bool:
    """Function to check whether an reported issue is related to a bug
    annotation."""

    # Check whether the issue kind and bug annotation kind are related
    if annot.annot_format == AnnotFormat.SMARTBUGS_FORMAT:
        if (
            issue.smartbugs_kind is None
            or annot.smartbugs_kind is None
            or issue.smartbugs_kind != annot.smartbugs_kind
        ):
            return False
    elif annot.annot_format == AnnotFormat.SMARTBENCH_FORMAT:
        # TODO: implement later
        return False

    # Check whether the issue and bug annotation are of the same file.
    return tool.match_location_of_issue_to_annotation(issue, annot)


def validate_issues(
    tool: Tool,
    issues: List[Issue],
    annots: List[BugAnnot],
) -> ValidationResult:
    """Validate detected issues against bug annotations in an input file."""

    # not used in solidifi
    correct_bugs: List[Tuple[Issue, BugAnnot]] = []
    unlabelled_issues: List[Issue] = []
    missing_bugs: List[BugAnnot] = []

    # First loop to detect correct bugs and missing bugs
    for annot in annots:
        # True-positive issues ==> correct bugs
        detected = False
        for issue in issues:
            if match_issue_to_annotation(tool, issue, annot):
                correct_bugs.append((issue, annot))
                detected = True
        if not detected:
            missing_bugs.append(annot)

    # Second loop to detect unlabelled_issues
    for issue in issues:
        matched_bug = False
        for annot in annots:
            if match_issue_to_annotation(tool, issue, annot):
                matched_bug = True
                break
        # Unknown issue
        if not matched_bug:
            unlabelled_issues.append(issue)

    return ValidationResult(correct_bugs, missing_bugs, unlabelled_issues)
