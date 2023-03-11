#!/usr/bin/env python3

"""Module for parsing results."""


# Standard Library
import os
import pathlib

from typing import Dict, List

# Third Party
import toml

# Library
from smartbench.debug import warning
from smartbench.issue import Issue, Severity
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


def process_analysis_result(tool: Tool, result_dir: str) -> List[Issue]:
    """Process analysis result of a tool."""
    process_result_fn = None

    if tool.is_slither():
        process_result_fn = slither.parse_slither_json_output

    if tool.is_confuzzius():
        process_result_fn = confuzzius.parse_confuzzius_json_output

    if process_result_fn:
        output_file = configure_output_file(tool, result_dir)
        return process_result_fn(output_file)

    return []


def is_test_result_directory(tool: Tool, test_dir: str) -> bool:
    """Check whether `test_dir` containing analysis result of a tool for
    a test file."""

    test_dir = os.path.abspath(test_dir)
    output_file = os.path.join(test_dir, tool.output_file)
    return os.path.exists(output_file)


def parse_existing_analysis_result(tool: Tool, test_dir: str) -> List[Issue]:
    """Parse a test result.

    The input `test_result_dir` is the directory containing the
    immediate result of an analysis tool.
    """

    test_dir = os.path.abspath(test_dir)
    output_file = os.path.join(test_dir, tool.output_file)
    # log_file = os.path.join(test_dir, tool.log_file)

    # with open(log_file, "r", encoding="utf-8") as file:
    #     file_content = file.read()
    #     print(f"content: {log_file}")
    #     log = toml.loads(file_content)
    #     input_log = log.get("input")
    #     if input_log is None:
    #         warning("Input information!")
    #     else:
    #         test_file = input_log.get("test_file")
    #         print(f"{'-' * 45}\n")
    #         print(f"Test file: {test_file}\n")

    parse_result_fn = None
    if tool.is_slither():
        parse_result_fn = slither.parse_slither_json_output

    if tool.is_confuzzius():
        parse_result_fn = confuzzius.parse_confuzzius_json_output

    if parse_result_fn is None:
        warning(f"Does not support parsing result of tool: {tool.name}")
        return []

    return parse_result_fn(output_file)


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
        for test_dir in test_dirs:
            test_file_name = os.path.basename(test_dir)

            if not is_test_result_directory(tool, test_dir):
                continue

            issues = parse_existing_analysis_result(tool, test_dir)
            for issue in issues:
                print(f"- {issue}")

            print_summary(test_file_name, issues)

            all_issues = all_issues + issues

    return all_issues
