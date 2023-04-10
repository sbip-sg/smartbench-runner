#!/usr/bin/env python3

"""Module for parsing results."""


# Standard Library
import os
import pathlib

from typing import Dict, List, Optional, Tuple

# Library
from smartbench import annotation, logger, validator
from smartbench.annotation import BugAnnot
from smartbench.issue import Issue, Severity
from smartbench.printer import warning
from smartbench.tools.config import load_tool_configuration
from smartbench.tools.confuzzius.confuzzius import Confuzzius
from smartbench.tools.mythril.mythril import Mythril
from smartbench.tools.sfuzz.sfuzz import Sfuzz
from smartbench.tools.slither.slither import Slither
from smartbench.tools.smartfuzz import smartfuzz
from smartbench.tools.smartian.smartian import Smartian
from smartbench.tools.tool import Tool
from smartbench.validator import Validation


class AnalysisResult:
    """Class capturing the validation result between detected issues and
    bug annotations in a smart contract."""

    def __init__(
        self,
        tool: Tool,
        test_file: str,
        issues: List[Issue],
        bug_annots: List[BugAnnot],
        validation: Optional[Validation],
    ):
        self.tool = tool
        self.test_file = test_file

        # All the issues that are reported
        self.issues: List[Issue] = list(issues)

        # Bug annotations specified for the test files.
        self.bug_annots: List[BugAnnot] = list(bug_annots)

        # Validation of detected issues
        self.validation = validation

    def print_summary(self):
        """Print statistic summary of detected issues for a test file"""
        print("-------------------------")
        print("ANALYSIS RESULT SUMMARY")
        print("-------------------------")
        print(f"- Tool: {self.tool.name}")
        print(f"- Test file: {self.test_file}")
        print(f"- Annotated bugs: {len(self.bug_annots)}")
        print(f"- Detected issues: {len(self.issues)}")

        # Print severity information
        severity_stat: Dict[Severity, int] = {}
        for issue in self.issues:
            if issue.severity in severity_stat:
                severity_stat[issue.severity] += 1
            else:
                severity_stat[issue.severity] = 1
        severity_info = [f"  + {s}: {severity_stat[s]}" for s in severity_stat]
        if len(severity_stat) > 0:
            print("\n".join(severity_info))

        # Print validation results
        if self.validation is not None:
            self.validation.print_summary()

        print("")


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

    if tool.is_smartfuzz():
        parse_result_fn = smartfuzz.parse_smartfuzz_json_output

    if parse_result_fn is None:
        warning(f"Does not support parsing result of tool: {tool.name}")
        return []

    return parse_result_fn(output_file, log_file)


def parse_result_directory(
    results_dir: str,
    validate=False,
    benchmarking=False,
    benchmark_name=None,
) -> List[AnalysisResult]:
    """Function to parse result directory of a tool.

    The input `result_dir` is the directory containing results of all
    tools.
    """
    print(f"Parsing result directory: {results_dir}")

    path = pathlib.Path(results_dir)
    if not path.is_dir():
        warning(f"Directory does not exists: {results_dir}")
        return []

    all_results: List[Issue] = []

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

            test_file = logger.get_input_test_file(log_file)
            print(f"{'-' * 45}\n")
            print(f"Test file: {test_file}\n")

            issues = []
            if (
                isinstance(tool, Slither)
                or isinstance(tool, Confuzzius)
                or isinstance(tool, Sfuzz)
                or isinstance(tool, Mythril)
                or isinstance(tool, Smartian)
            ):
                issues = tool.parse_analysis_output(test_output_dir)
            else:
                issues = parse_existing_analysis_result(
                    tool, output_file, log_file
                )

            for issue in issues:
                print(f"- {issue}")

            bug_annots = []
            validation = None
            if validate or benchmarking:
                if test_file is None:
                    print(f"Unable to read test file: {test_file}")
                    print("Skip validating results!")
                else:
                    print("Bug annotations:")
                    bug_annots = annotation.parse_bug_annotations(
                        test_file, annot_format=benchmark_name
                    )
                    annotations += len(bug_annots)
                    for annot in bug_annots:
                        print(f"- {annot.print_concise()}")

                    validation = validator.validate_issues(
                        tool,
                        test_file,
                        issues,
                        bug_annots,
                        benchmark_name=benchmark_name or "",
                    )
                    correct_bugs += validation.num_correct_bugs()
                print("")

            ares = AnalysisResult(
                tool, test_file, issues, bug_annots, validation
            )
            ares.print_summary()
            all_results.append(ares)

        if validate:
            print(f"Result for {tool_id} is {correct_bugs}/{annotations}")

    print("Parsing result completed!")
    return all_results


def parse_instruction_coverage(results_dir: str):
    """Function to parse code coverage from analysis results of a tool.

    The input `result_dir` is the directory containing results of all
    tools.
    """

    path = pathlib.Path(results_dir)
    if not path.is_dir():
        warning(f"Directory does not exists: {results_dir}")
        return

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

        if not (
            isinstance(tool, Sfuzz)
            or isinstance(tool, Confuzzius)
            or isinstance(tool, Smartian)
        ):
            print(f"Parse coverage is not supported for: {tool.id}")
            continue

        print(f"{'=' * 55}\n")
        print(f"Parsing analysis result of: {tool.id}\n")

        tool_output_dir = os.path.join(results_dir, tool_id)
        test_output_dirs = sorted([p[0] for p in os.walk(tool_output_dir)])
        for test_output_dir in test_output_dirs:
            if not is_test_result_directory(tool, test_output_dir):
                continue

            if (
                isinstance(tool, Sfuzz)
                or isinstance(tool, Confuzzius)
                or isinstance(tool, Smartian)
            ):
                coverage = tool.parse_instruction_coverage(test_output_dir)
                print(f"test_output_dir: {test_output_dir}")
                print(f"coverage: {coverage}")

    print("Parsing result completed!")
    return all_issues
