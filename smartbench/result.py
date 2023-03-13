#!/usr/bin/env python3

"""Module for parsing results."""


# Standard Library
import os
import pathlib

from typing import Dict, List

# Library
from smartbench import bug_annot
from smartbench.bug_annot import BugAnnot
from smartbench import log
from smartbench.debug import warning
from smartbench.issue import Issue, Severity, IssueKind
from smartbench.tools.slither import slither
from smartbench.tools.confuzzius import confuzzius
from smartbench.tools.tool import (
    Tool,
    configure_output_file,
    load_tool_configuration,
)


def print_summary(test_file_name: str, issues: List[Issue]):
    """Print statistic summary of detected issues for a test file"""
    print(f"Summary for {test_file_name}:")
    print(f"- Number of issues: {len(issues)}")

    severities: Dict[Severity, int] = {}
    for issue in issues:
        if issue.severity in severities:
            severities[issue.severity] += 1
        else:
            severities[issue.severity] = 1
    severity = ", ".join([f"{s}: {severities[s]}" for s in severities])
    print(f"- Severity: {severity}\n")


def process_analysis_result(tool: Tool, output_dir: str) -> List[Issue]:
    """Process analysis result of a tool."""
    process_result_fn = None

    if tool.is_slither():
        process_result_fn = slither.parse_slither_json_output

    if tool.is_confuzzius():
        process_result_fn = confuzzius.parse_confuzzius_json_output

    if process_result_fn:
        output_file = os.path.join(output_dir, tool.output_file)
        log_file = os.path.join(output_dir, tool.log_file)
        try:
            return process_result_fn(output_file, log_file);
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


def check_detected_issue(annot: BugAnnot, issues: List[Issue]) -> bool:
    category = annot.bug_name.casefold()
    line = annot.start_line + 1
    for issue in issues:
        if issue.location != None:
            kind = issue.issue_kind
            location = issue.location.start_line
            if line <= location and location <= line + 5:
                if category == "arithmetic" and kind == IssueKind.INTEGER_OVERFLOW:
                    return True;
                if category == "arithmetic" and kind == IssueKind.INTEGER_UNDERFLOW:
                    return True;
                if category == "bad_randomness" and kind == IssueKind.BLOCK_DEPENDENCY:
                    return True;
                if category == "time_manipulation" and kind == IssueKind.BLOCK_DEPENDENCY:
                    return True;
                if category == "front_running" and kind == IssueKind.TRANSACTION_ORDER_DEPENDENCY:
                    return True;
                if category == "transaction_order_dependency" and kind == IssueKind.TRANSACTION_ORDER_DEPENDENCY:
                    return True;
                if category == "unchecked_ll_calls" and kind == IssueKind.UNHANDLED_EXCEPTION:
                    return True;
                if str(kind).casefold() == category:
                    return True;
    return False;


def parse_existing_analysis_result(tool: Tool, test_dir: str) -> (List[Issue], List[BugAnnot]):
    """Parse a test result.

    The input `test_result_dir` is the directory containing the
    immediate result of an analysis tool.
    """

    test_dir = os.path.abspath(test_dir)
    output_file = os.path.join(test_dir, tool.output_file)
    log_file = os.path.join(test_dir, tool.log_file)
    test_file = log.get_input_test_file(log_file)
    annots = []
    print(f"Test file: {test_file}\n")
    annots = bug_annot.parse_bug_annotations(test_file)

    parse_result_fn = None
    if tool.is_slither():
        parse_result_fn = slither.parse_slither_json_output

    if tool.is_confuzzius():
        parse_result_fn = confuzzius.parse_confuzzius_json_output

    if parse_result_fn is None:
        warning(f"Does not support parsing result of tool: {tool.name}")
        return []

    issues = parse_result_fn(output_file, log_file)
    return (issues, annots)

def parse_result_directory(result_dir: str) -> List[Issue]:
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
        total_bugs = 0
        validated_bugs = 0
        for test_dir in test_dirs:
            test_file_name = os.path.basename(test_dir)

            if not is_test_result_directory(tool, test_dir):
                continue

            issues, annots = parse_existing_analysis_result(tool, test_dir)
            total_bugs += len(annots)
            for annot in annots:
                if check_detected_issue(annot, issues):
                    validated_bugs += 1
                print(annot.print_by_line())

            for issue in issues:
                print(f"- {issue}")

            print_summary(test_file_name, issues)

            all_issues = all_issues + issues

        print(f"validation: {validated_bugs}/{total_bugs}")

    return all_issues
