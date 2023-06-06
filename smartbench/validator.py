#!/usr/bin/env python3

"""Module to validate analysis results with bug annotations."""

# Standard Library
from json import encoder
from typing import List, Tuple

# Third Party
import more_itertools as mit

# Library
from smartbench.annotation import AnnotFormat, BugAnnot
from smartbench.issue import Issue, IssueKind
from smartbench.printer import debug, safe_print
from smartbench.tools.tool import Tool

# Global stats, don't share among threads
global_stats = {
    # tools_name -> a dict:
    # {
    #     'n_files': 0,
    #     'n_unlabeled': 0,
    #     'n_unlabeled_average': 0,
    #     'n_by_bug_type':{}, # unlabeled bug-type -> unlabeld count
    # }
}

class ValidationResult:
    def __init__(
        self,
        test_file: str,
        tool: Tool,
        correct_bugs: List[Tuple[Issue, BugAnnot]], # TP for all bug types
        missing_bugs: List[BugAnnot],               # FN for all bug types
        unlabelled_issues: List[Issue],
    ):
        self.test_file = test_file
        self.tool = tool

        # Issues that are reported.
        self.correct_bugs: List[(Issue, BugAnnot)] = list(correct_bugs)

        # Bug annotations that are not reported.
        self.missing_bugs: List[BugAnnot] = list(missing_bugs)

        # Issues unrelated to bug annotations.
        self.unlabelled_issues: List[Issue] = list(unlabelled_issues)

        self.stats()

    def num_correct_bugs(self) -> int:
        return len(self.correct_bugs)

    def print_summary(self) -> None:
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
            unlabelled_info += f" [Issue IDs: {print_indices(unlabelled_idxs)}]"
        safe_print(f"  + Unlabelled issues: {unlabelled_info}")

    def stats(self) -> dict:
        r = {}
        global global_stats
        tool_key = self.tool.name.lower() # which tool we are using
        annot_key = self.missing_bugs and self.missing_bugs[0].annot_format
        annot_key = annot_key or (self.correct_bugs and self.correct_bugs[0][1].annot_format)
        annot_key = str(annot_key.value).lower() # which annotation (test database) we are using. Assuing one ValidationResult object won't have multiple annotation databases

        if tool_key not in global_stats:
            global_stats[tool_key] = {
                'n_files': 0,
                'n_unlabeled': 0,
                'n_unlabeled_average': 0,
                'n_by_bug_type':{}, # unlabeled bug-type -> unlabeld count
            }

        for (issue, _bug) in self.correct_bugs:
            inc_in_path(r, 'num_detected_in_annot', str(issue.issue_kind))

        for bug in self.missing_bugs:
            inc_in_path(r, 'num_not_detected_in_annot', bug.annot_name)

        r['unlabeled'] = sorted(list(self.unlabelled_issues))

        for issue in self.unlabelled_issues:
            inc_in_path(r, 'num_detected_not_in_annot', str(issue.issue_kind))
            inc_in_path(global_stats, tool_key, 'n_by_bug_type', str(issue.issue_kind))

        global_stats[tool_key]['n_files'] += 1
        global_stats[tool_key]['n_unlabeled'] += len(self.unlabelled_issues)
        global_stats[tool_key]['n_unlabeled_average'] = global_stats[tool_key]['n_unlabeled'] / global_stats[tool_key]['n_files']

        f_stats = f'{self.test_file}_{tool_key}_stats.csv'
        print(f'Detected bugs not in annotation for {self.test_file}\n Stats csv written to {f_stats}')
        for issue in self.unlabelled_issues:
            locs = ' '.join([str(s) for s in issue.locations])
            print(f'{issue.index} {issue.issue_kind} {locs}')
        with open(f_stats, 'w') as f:
            f.write('file_name,bug_type,original_bug_type,locations,summary\n')
            del r['unlabeled']
            f.write(f',,,,{r}\n')
            for issue in self.unlabelled_issues:
                locs = ' '.join([str(s) for s in issue.locations])
                f.write(f'{self.test_file},{issue.issue_kind.value},{issue.issue_kind.original_type},{locs},\n')
            f.flush()


        f_global_stats = f'{tool_key}_{annot_key}_global_stats.csv'
        with open(f_global_stats, 'w') as f:
            import json
            f.write(json.dumps(global_stats[tool_key], indent=2))
        return r



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
    if annot.annot_format == AnnotFormat.SMARTBUGS:
        if (
            issue.smartbugs_pp_kind is None
            or annot.smartbugs_kind is None
            or issue.smartbugs_pp_kind != annot.smartbugs_kind
        ):
            return False
    elif annot.annot_format == AnnotFormat.SOLIDIFI:
        if (
            issue.solidifi_pp_kind is None
            or annot.solidifi_kind is None
            or issue.solidifi_pp_kind != annot.solidifi_kind
        ):
            return False
    elif annot.annot_format == AnnotFormat.SMARTBENCH:
        if (
            issue.smartbench_kind is None
            or annot.smartbench_kind is None
            or issue.smartbench_kind != annot.smartbench_kind
        ):
            return False

    elif annot.annot_format == AnnotFormat.VERISMART:
        if (
            issue.verismart_kind is None
            or annot.verismart_kind is None
            or issue.verismart_kind != annot.verismart_kind
        ):
            return False

    # Check whether the issue and bug annotation are of the same file.
    return tool.match_location_of_issue_to_annotation(issue, annot)


def validate_issues(
    test_file: str,
    tool: Tool,
    issues: List[Issue],
    annots: List[BugAnnot],
) -> ValidationResult:
    """Validate detected issues against bug annotations in an input file."""

    # not used in solidifi
    correct_bugs: List[Tuple[Issue, BugAnnot]] = []
    unlabelled_issues: List[Issue] = []
    missing_bugs: List[BugAnnot] = []

    # Detect correct bugs
    for issue in issues:
        detected = False
        for annot in annots:
            if annot.is_real_bug and match_issue_to_annotation(
                tool, issue, annot
            ):
                correct_bugs.append((issue, annot))
                break

    # Detect missing bugs
    for annot in annots:
        if not annot.is_real_bug:
            continue

        detected = False
        for issue in issues:
            if match_issue_to_annotation(tool, issue, annot):
                # issues must be sorted ascending by detected_time
                # this matches the earliest time the annot is detected
                annot.time_detected = issue.time_detected
                detected = True
                break
        if not detected:
            missing_bugs.append(annot)

    # Detect unlabelled issues
    for issue in issues:
        detected = False
        for annot in annots:
            if annot.is_real_bug and match_issue_to_annotation(
                tool, issue, annot
            ):
                detected = True
                break
        if (not detected) and (issue not in unlabelled_issues):
            unlabelled_issues.append(issue)

    return ValidationResult(test_file, tool, correct_bugs, missing_bugs, unlabelled_issues)


def inc_in_path(d, *keys):
    if len(keys) == 0:
        return d

    key = keys[0]
    if key not in d:
        if len(keys) == 1:
            d[key] = 0
        else:
            d[key] = {}

    if len(keys) == 1:
        d[key] += 1
    else:
        inc_in_path(d[key], *keys[1:])
    return d
