#!/usr/bin/env python3

"""Module for parsing results."""


# Standard Library
import os
import pathlib

from typing import Dict, List, Optional

# Third Party
import more_itertools as mit

# Library
from smartbench import bug_annot, log, validator
from smartbench.bug_annot import BugAnnot
from smartbench.debug import warning
from smartbench.issue import Issue, Severity
from smartbench.tools.config import load_tool_configuration
from smartbench.tools.confuzzius import confuzzius
from smartbench.tools.mythril import mythril
from smartbench.tools.sfuzz import sfuzz
from smartbench.tools.slither import slither
from smartbench.tools.slither.slither import Slither
from smartbench.tools.smartfuzz import smartfuzz
from smartbench.tools.smartian import smartian
from smartbench.tools.tool import Tool
from smartbench.validator import ValidationResult


def print_indices(indices: List[int]) -> str:
    index_groups = [list(group) for group in mit.consecutive_groups(indices)]
    groups = [
        f"{group[0]}-{group[-1]}" if len(group) > 1 else f"{group[0]}"
        for group in index_groups
    ]
    return ", ".join(groups)


def print_summary(
    tool: Tool,
    test_name: str,
    issues: List[Issue],
    annots: Optional[List[BugAnnot]] = None,
    validation: Optional[ValidationResult] = None,
):
    """Print statistic summary of detected issues for a test file"""
    print("------------------")
    print("ANALYSIS SUMMARY")
    print("------------------")
    print(f"- Tool: {tool.name}")
    print(f"- Contract: {test_name}")

    # Print bug annotations
    if annots is not None:
        print(f"- Annotated bugs: {len(annots)}")

    # Print issues details
    print(f"- Detected issues: {len(issues)}")
    severities: Dict[Severity, int] = {}
    for issue in issues:
        if issue.severity in severities:
            severities[issue.severity] += 1
        else:
            severities[issue.severity] = 1
    severities = [f"  + {s}: {severities[s]}" for s in severities]
    if len(severities) > 0:
        print("\n".join(severities))

    # Print validation results
    if validation is not None:
        print("- Validation:")

        correct_issue_info = f"{len(validation.correct_issues)}"
        correct_idxs = [x.index for x in validation.correct_issues]
        if len(correct_idxs) > 0:
            correct_issue_info += f" [Issue IDs: {print_indices(correct_idxs)}]"
        print(f"  + Correct issues: {correct_issue_info}")

        wrong_issue_info = f"{len(validation.incorrect_issues)}"
        wrong_idxs = [x.index for x in validation.incorrect_issues]
        if len(wrong_idxs) > 0:
            wrong_issue_info += f" [Issue IDs: {print_indices(wrong_idxs)}]"
        print(f"  + Wrong issues: {wrong_issue_info}")

        print(f"  + Unknown issues: {len(validation.unknown_issues)}")

        missing_bug_info = f"{len(validation.missing_bugs)}"
        missing_idxs = [x.index for x in validation.missing_bugs]
        if len(missing_idxs) > 0:
            missing_bug_info += f" [Bug IDs: {print_indices(missing_idxs)}]"
        print(f"  + Missing bugs: {missing_bug_info}")

    print("")


def process_analysis_result(tool: Tool, test_output_dir: str) -> List[Issue]:
    """Process analysis result of a tool for a test file."""
    # TODO: Make this function OOP
    process_result_fn = None

    if isinstance(tool, Slither):
        return tool.process_analysis_result(test_output_dir)

    if tool.is_smartfuzz():
        process_result_fn = smartfuzz.parse_smartfuzz_json_output

    if tool.is_confuzzius():
        process_result_fn = confuzzius.parse_confuzzius_json_output

    if tool.is_sfuzz():
        process_result_fn = sfuzz.parse_sfuzz_json_output

    if tool.is_mythril():
        process_result_fn = mythril.parse_mythril_json_output

    if tool.is_smartian():
        process_result_fn = smartian.parse_analysis_output

    if process_result_fn:
        output_file = os.path.join(test_output_dir, tool.output_file)
        log_file = os.path.join(test_output_dir, tool.log_file)
        try:
            return process_result_fn(output_file, log_file)
        except:
            # When there is no results
            return []

    return []


def is_test_result_directory(tool: Tool, test_dir: str) -> bool:
    """Check whether `test_dir` containing analysis result of a tool for
    a test file."""

    test_dir = os.path.abspath(test_dir)
    output_file = os.path.join(test_dir, tool.output_file)
    return os.path.exists(output_file)


def parse_existing_analysis_result(
    tool: Tool, output_file: str, log_file: str
) -> List[Issue]:
    """Parse a test result.

    The input `test_result_dir` is the directory containing the
    immediate result of an analysis tool.
    """

    # Reset issue index counter for the current output file
    Issue.index_counter = 1

    parse_result_fn = None

    if tool.is_slither():
        parse_result_fn = slither.parse_slither_json_output

    if tool.is_smartfuzz():
        parse_result_fn = smartfuzz.parse_smartfuzz_json_output
    if tool.is_confuzzius():
        parse_result_fn = confuzzius.parse_confuzzius_json_output

    if tool.is_sfuzz():
        parse_result_fn = sfuzz.parse_sfuzz_json_output

    if tool.is_mythril():
        parse_result_fn = mythril.parse_mythril_json_output

    if tool.is_smartian():
        parse_result_fn = smartian.parse_analysis_output

    if parse_result_fn is None:
        warning(f"Does not support parsing result of tool: {tool.name}")
        return []

    return parse_result_fn(output_file, log_file)


def parse_result_directory(
    results_dir: str, validate_results=False
) -> List[Issue]:
    """Function to parse result directory of a tool.

    The input `result_dir` is the directory containing results of all
    tools.
    """

    path = pathlib.Path(results_dir)
    if not path.is_dir():
        warning(f"Directory does not exists: {results_dir}")
        return []

    all_issues: List[Issue] = []

    # Parse results of each analysis tool
    items = list(os.listdir(results_dir))
    for item in items:
        item_path = os.path.join(results_dir, item)
        if not os.path.isdir(item_path):
            continue

        # Tool ID is assumed to be the same as tool_dir
        tool_id = item
        tool = load_tool_configuration(tool_id)

        if tool is None:
            warning(f"Unable to load tool configuration: {tool_id}")
            continue

        print(f"{'=' * 55}\n")
        print(f"Parsing analysis result of: {tool.id}\n")

        tool_output_dir = os.path.join(results_dir, tool_id)
        test_output_dirs = sorted([p[0] for p in os.walk(tool_output_dir)])
        correct_bugs = 0
        annotations = 0
        for test_output_dir in test_output_dirs:
            if not is_test_result_directory(tool, test_output_dir):
                continue

            test_output_dir = os.path.abspath(test_output_dir)
            output_file = os.path.join(test_output_dir, tool.output_file)
            log_file = os.path.join(test_output_dir, tool.log_file)

            test_file = log.get_input_test_file(log_file)
            print(f"{'-' * 45}\n")
            print(f"Test file: {test_file}\n")

            issues = parse_existing_analysis_result(tool, output_file, log_file)
            for issue in issues:
                print(f"- {issue}")

            bug_annots = None
            validation = None
            test_name = os.path.basename(test_output_dir)
            if validate_results:
                if test_file is None:
                    print(f"Unable to read test file: {test_file}")
                    print("Skip validating results!")
                else:
                    print("Bug annotations:")
                    bug_annots = bug_annot.parse_bug_annotations(test_file)
                    annotations += len(bug_annots)
                    for annot in bug_annots:
                        print(f"- {annot.print_concise()}")

                    validation = validator.validate_issues(
                        tool, test_file, issues
                    )
                    correct_bugs += len(validation.correct_issues)
                print("")
            print_summary(tool, test_name, issues, bug_annots, validation)
            all_issues = all_issues + issues

        if validate_results:
            print(f"Result for {tool_id} is {correct_bugs}/{annotations}")

    print("Parsing result completed!")
    return all_issues
