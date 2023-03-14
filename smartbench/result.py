#!/usr/bin/env python3

"""Module for parsing results."""


# Standard Library
import os
import pathlib

from typing import Dict, List, Union

# Library
from smartbench import bug_annot, log, validate
from smartbench.bug_annot import BugAnnot
from smartbench.debug import warning
from smartbench.issue import Issue, Severity
from smartbench.tools.slither import slither
from smartbench.tools.tool import Tool, load_tool_configuration
from smartbench.validate import Validation


def print_summary(
    tool: Tool,
    test_name: str,
    issues: List[Issue],
    annots: Union[List[BugAnnot], None] = None,
    validation: Union[Validation, None] = None,
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
    severity = "\n  + ".join([f"{s}: {severities[s]}" for s in severities])
    print(f"  + {severity}")

    # Pritn validation results
    if validation is not None:
        print("- Validation:")
        print(f"  + Correct issues: {len(validation.correct_issues)}")
        print(f"  + Wrong issues: {len(validation.incorrect_issues)}")
        print(f"  + Unknown issues: {len(validation.unknown_issues)}")
        print(f"  + Missing bugs: {len(validation.missing_bugs)}")

    print("")


def process_analysis_result(tool: Tool, output_dir: str) -> List[Issue]:
    """Process analysis result of a tool."""
    process_result_fn = None

    if tool.is_slither():
        process_result_fn = slither.parse_slither_json_output

    if process_result_fn:
        output_file = os.path.join(output_dir, tool.output_file)
        log_file = os.path.join(output_dir, tool.log_file)
        return process_result_fn(output_file, log_file)

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

    parse_result_fn = None
    if tool.is_slither():
        parse_result_fn = slither.parse_slither_json_output

    if parse_result_fn is None:
        warning(f"Does not support parsing result of tool: {tool.name}")
        return []

    return parse_result_fn(output_file, log_file)


def parse_result_directory(
    result_dir: str, validate_results=False
) -> List[Issue]:
    """Function to parse result directory of a tool.

    The input `result_dir` is the directory containing results of all
    tools.
    """

    path = pathlib.Path(result_dir)
    if not path.is_dir():
        warning(f"Directory does not exists: {result_dir}")
        return []

    all_issues: List[Issue] = []

    # Parse results of each analysis tool
    items = list(os.listdir(result_dir))
    for item in items:
        item_path = os.path.join(result_dir, item)
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

        tool_dir = os.path.join(result_dir, tool_id)
        test_dirs = [p[0] for p in os.walk(tool_dir)]
        test_dirs = sorted(test_dirs)
        for test_dir in test_dirs:
            if not is_test_result_directory(tool, test_dir):
                continue

            test_dir = os.path.abspath(test_dir)
            output_file = os.path.join(test_dir, tool.output_file)
            log_file = os.path.join(test_dir, tool.log_file)

            test_file = log.get_input_test_file(log_file)
            print(f"{'-' * 45}\n")
            print(f"Test file: {test_file}\n")

            issues = parse_existing_analysis_result(tool, output_file, log_file)
            for issue in issues:
                print(f"- {issue}")

            bug_annots = None
            validation = None
            test_name = os.path.basename(test_dir)
            if validate_results:
                if test_file is None:
                    print(f"Unable to read test file: {test_file}")
                    print("Skip validating results!")
                else:
                    print("Bug annotations:")
                    bug_annots = bug_annot.parse_bug_annotations(test_file)
                    for annot in bug_annots:
                        print(f"- {annot.print_by_line()}")
                    validation = validate.validate_issues(test_file, issues)
                print("")
            print_summary(tool, test_name, issues, bug_annots, validation)
            all_issues = all_issues + issues

    print("Parsing result completed!")

    return all_issues
